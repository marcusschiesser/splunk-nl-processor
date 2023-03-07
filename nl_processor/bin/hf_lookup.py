import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import (
    dispatch,
    StreamingCommand,
    Configuration,
    Option,
    validators,
)

from urllib.error import HTTPError
import requests
import copy
from splunklib import client
from passwords import decode_password

PAYLOAD_KEY = "payload"


@Configuration()
class HfLookupCommand(StreamingCommand):
    api_token = None
    model = Option(name="model", require=True)
    maxcalls = Option(
        name="maxcalls", default=100, require=False, validate=validators.Integer(1)
    )
    continue_on_errors = Option(
        name="continue_on_errors",
        default=False,
        require=False,
        validate=validators.Boolean(),
    )

    def query(self, payload):
        """Calls the Huggingface Inference API
        :raises HTTPError: Raised for unsuccessful queries.
        """
        headers = {"Authorization": f"Bearer {self.api_token}"}
        API_URL = f"https://api-inference.huggingface.co/models/{self.model}"
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    def stream(self, records):
        session_key = self.metadata.searchinfo.session_key
        app_name = self.metadata.searchinfo.app
        service = client.Service(token=session_key, app=app_name)
        self.api_token = decode_password(service, "api_token")
        # Run saved search for each input record
        for index, record in enumerate(records):
            if index == self.maxcalls:
                self.logger.warning(
                    f"Reached limit of max. {self.maxcalls} API calls. Skipping remaining records. Try increasing the `maxcalls` argument."
                )
                break
            try:
                payload = record[PAYLOAD_KEY]
                results = self.query(payload)
                self.logger.info(
                    f'msg="Successfully called HF inference API" model="{self.model}" payload="{payload}"'
                )
                # ensure that results is a list
                if not isinstance(results, list):
                    results = [results]
                # iterate over results list
                for result in results:
                    if not isinstance(result, list):
                        result = [result]
                    for subresult in result:
                        new_record = copy.deepcopy(record)
                        for key, value in subresult.items():
                            new_record[key] = value
                        yield new_record
            except HTTPError as he:
                if self.continue_on_errors:
                    self.logger.error(
                        f'msg="Failed to call HF inference API. Continuing as continue_on_errors=true." model="{self.model}" payload="{payload}" error="{str(he)}"'
                    )
                else:
                    raise he


dispatch(HfLookupCommand, sys.argv, sys.stdin, sys.stdout, __name__)
