import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from splunklib import client
from splunk.persistconn.application import PersistentServerConnectionApplication
from passwords import encode_password, decode_password


def flatten_query_params(params):
    flattened = {}
    for i, j in params:
        flattened[i] = flattened.get(i) or j
    return flattened


def is_unchanged_password(text):
    return all(char == "*" for char in text)


class ConfigureHandler(PersistentServerConnectionApplication):
    def __init__(self, _command_line, _command_arg):
        PersistentServerConnectionApplication.__init__(self)

    def handle(self, in_string):
        try:
            request = json.loads(in_string)
            service = client.Service(
                token=request["system_authtoken"], sharing="app", app="nl_processor"
            )

            if request["method"] == "POST":
                payload = flatten_query_params(request["form"])
                return self.handle_post(service, payload)
            else:
                return self.handle_get(service)
        except Exception as ex:
            import traceback

            return {
                "payload": {
                    "success": "false",
                    "message": f"Error: {repr(ex)}",
                    "traceback": traceback.format_exc(),
                },
                "status": 500,
            }

    def handle_get(self, service):
        conf = service.confs["commands"]
        stanza = conf["openai"]

        azure_resource_name = (
            stanza["azure_resource_name"] if "azure_resource_name" in stanza else ""
        )
        hf_api_token = "***" if decode_password(service, "hf_api_token") else ""
        openai_api_key = "***" if decode_password(service, "openai_api_key") else ""

        return {
            "payload": {
                "success": "true",
                "azure_resource_name": azure_resource_name,
                "hf_api_token": hf_api_token,
                "openai_api_key": openai_api_key,
            },
            "status": 200,
        }

    def handle_post(self, service, payload):
        try:
            hf_api_token = payload["hf_api_token"]
            openai_api_key = payload["openai_api_key"]
            azure_resource_name = payload["azure_resource_name"]

            conf = service.confs["commands"]
            stanza = conf["openai"]
            stanza.submit({"azure_resource_name": azure_resource_name})

            if not is_unchanged_password(hf_api_token):
                encode_password(service, "hf_api_token", hf_api_token)
            if not is_unchanged_password(openai_api_key):
                encode_password(service, "openai_api_key", openai_api_key)

            return {"payload": {"success": "true"}, "status": 200}
        except (KeyError, ValueError) as e:
            return {
                "payload": {"success": "false", "result": f"Error parsing JSON: {e}"},
                "status": 400,
            }
