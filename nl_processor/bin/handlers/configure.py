import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from splunklib import client
from splunk.persistconn.application import PersistentServerConnectionApplication
from passwords import encode_password


def flatten_query_params(params):
    flattened = {}
    for i, j in params:
        flattened[i] = flattened.get(i) or j
    return flattened


class ConfigureHandler(PersistentServerConnectionApplication):
    def __init__(self, _command_line, _command_arg):
        PersistentServerConnectionApplication.__init__(self)

    def handle(self, in_string):
        try:
            request = json.loads(in_string)
            payload = flatten_query_params(request["form"])
            api_token = payload["api_token"]

            service = client.Service(
                token=request["system_authtoken"], sharing="app", app="nl_processor"
            )
            encode_password(service, "api_token", api_token)

            return {"payload": {"success": "true"}, "status": 200}
        except (KeyError, ValueError) as e:
            return {
                "payload": {"success": "false", "result": f"Error parsing JSON: {e}"},
                "status": 400,
            }
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
