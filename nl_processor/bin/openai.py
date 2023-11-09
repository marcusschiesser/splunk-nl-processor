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

EMBEDDINGS = "embeddings"
COMPLETIONS = "completions"

MODELS = {
    EMBEDDINGS: "text-embedding-ada-002",
    COMPLETIONS: "text-davinci-003",
}

AZURE_API_VERSION = "2023-05-15"


@Configuration()
class OpenAI(StreamingCommand):
    openai_api_key = None
    azure_resource_name = None
    type = Option(
        name="type",
        default=EMBEDDINGS,
        require=False,
        validate=validators.Set(EMBEDDINGS, COMPLETIONS),
    )

    input_field = Option(
        name="input",
        default="input",
        require=False,
        validate=validators.Fieldname(),
    )
    input = Option(name="input_text", require=False)
    output_field = Option(
        name="output",
        default="result",
        require=False,
        validate=validators.Fieldname(),
    )

    maxcalls = Option(
        name="maxcalls", default=100, require=False, validate=validators.Integer(0)
    )
    continue_on_errors = Option(
        name="continue_on_errors",
        default=False,
        require=False,
        validate=validators.Boolean(),
    )
    deployment_id = Option(name="deployment_id", require=False)
    model = Option(name="model", require=False)

    def call_openai_api(self, endpoint, payload):
        """Calls the OpenAI API
        :raises HTTPError: Raised for unsuccessful queries.
        """
        if self.azure_resource_name:
            if not self.deployment_id:
                raise Exception(
                    "Specify deployment_id if running OpenAI command on Azure"
                )
            headers = {
                "api-key": self.openai_api_key,
                "Content-Type": "application/json",
            }
            api_url = f"https://{self.azure_resource_name}.openai.azure.com/openai/deployments/{self.deployment_id}/{endpoint}?api-version={AZURE_API_VERSION}"
        else:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            }
            api_url = f"https://api.openai.com/v1/{endpoint}"

        response = requests.post(api_url, headers=headers, json=payload)
        self.logger.info(
            f'msg="Successfully called OpenAI {endpoint} API" model="{payload.get("model")}" input_text="{payload.get("input", payload.get("prompt"))}"'
        )
        return response.json()

    def get_embedding(self, input):
        payload = {
            "input": input,
            "model": self.model if self.model else MODELS[EMBEDDINGS],
        }
        json = self.call_openai_api(EMBEDDINGS, payload)
        if "error" in json:
            return json["error"]["message"]
        return json["data"][0]["embedding"]

    def get_completion(self, input):
        payload = {
            "prompt": input,
            "model": self.model if self.model else MODELS[COMPLETIONS],
            "temperature": 0,
            "max_tokens": 100,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }
        json = self.call_openai_api(COMPLETIONS, payload)
        if "error" in json:
            return json["error"]["message"]
        return json["choices"][0]["text"]

    def get_result(self, input):
        if self.type == EMBEDDINGS:
            return self.get_embedding(input)
        elif self.type == COMPLETIONS:
            return self.get_completion(input)

    def stream(self, records):
        session_key = self.metadata.searchinfo.session_key
        app_name = self.metadata.searchinfo.app
        service = client.Service(token=session_key, app=app_name)
        self.openai_api_key = decode_password(service, "openai_api_key")
        conf = service.confs["commands"]
        stanza = conf["openai"]
        self.azure_resource_name = (
            stanza["azure_resource_name"] if "azure_resource_name" in stanza else None
        )
        # if input is specified, use it to call the OpenAI API directly
        if self.input:
            result = self.get_result(self.input)
        # Run saved search for each input record
        for index, record in enumerate(records):
            if not self.input:
                if self.maxcalls != 0 and index == self.maxcalls:
                    self.logger.warning(
                        f"Reached limit of max. {self.maxcalls} API calls. Skipping remaining records. Try increasing the `maxcalls` argument."
                    )
                    break
                try:
                    input = record[self.input_field]
                    result = self.get_result(input)
                except HTTPError as he:
                    if self.continue_on_errors:
                        self.logger.error(
                            f'msg="Failed to call OpenAI API. Continuing as continue_on_errors=true." type="{self.type}" input_text="{input}" error="{str(he)}"'
                        )
                    else:
                        raise he
            new_record = copy.deepcopy(record)
            new_record[self.output_field] = result
            yield new_record


dispatch(OpenAI, sys.argv, sys.stdin, sys.stdout, __name__)
