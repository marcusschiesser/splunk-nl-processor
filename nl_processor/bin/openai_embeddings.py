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


@Configuration()
class OpenAIEmbeddingCommand(StreamingCommand):
    openai_api_key = None
    model = Option(name="model", default="text-embedding-ada-002", require=False)
    input_field = Option(
        name="input_field", require=True, validate=validators.Fieldname()
    )

    maxcalls = Option(
        name="maxcalls", default=100, require=False, validate=validators.Integer(1)
    )
    continue_on_errors = Option(
        name="continue_on_errors",
        default=False,
        require=False,
        validate=validators.Boolean(),
    )

    def get_embedding(self, input):
        """Calls the OpenAI API for calculating embeddings
        :raises HTTPError: Raised for unsuccessful queries.
        """
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        API_URL = "https://api.openai.com/v1/embeddings"
        response = requests.post(
            API_URL, headers=headers, json={"input": input, "model": self.model}
        )
        json = response.json()
        if "error" in json:
            return json["error"]["message"] 
        return json["data"][0]["embedding"]

    def stream(self, records):
        session_key = self.metadata.searchinfo.session_key
        app_name = self.metadata.searchinfo.app
        service = client.Service(token=session_key, app=app_name)
        self.openai_api_key = decode_password(service, "openai_api_key")
        # Run saved search for each input record
        for index, record in enumerate(records):
            if index == self.maxcalls:
                self.logger.warning(
                    f"Reached limit of max. {self.maxcalls} API calls. Skipping remaining records. Try increasing the `maxcalls` argument."
                )
                break
            try:
                input = record[self.input_field]
                embedding = self.get_embedding(input)
                self.logger.info(
                    f'msg="Successfully called OpenAI embedding API" model="{self.model}" input_text="{input}"'
                )
                new_record = copy.deepcopy(record)
                new_record["embedding"] = embedding
                yield new_record
            except HTTPError as he:
                if self.continue_on_errors:
                    self.logger.error(
                        f'msg="Failed to call OpenAI embedding API. Continuing as continue_on_errors=true." model="{self.model}" input_text="{input}" error="{str(he)}"'
                    )
                else:
                    raise he


dispatch(OpenAIEmbeddingCommand, sys.argv, sys.stdin, sys.stdout, __name__)
