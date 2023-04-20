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
import copy


@Configuration()
class DotProductCommand(StreamingCommand):
    vector1 = Option(name="vector1", require=True, validate=validators.Fieldname())
    vector2 = Option(name="vector2", require=True, validate=validators.Fieldname())
    output = Option(name="output", default="output", validate=validators.Fieldname())

    def stream(self, records):
        for record in records:
            vector1 = record[self.vector1]
            if not isinstance(vector1, list):
                vector1 = vector1.split()
            vector2 = record[self.vector2]
            if not isinstance(vector2, list):
                vector2 = vector2.split()
            try:
                vector1_list = [float(x) for x in vector1]
                vector2_list = [float(x) for x in vector2]
                dot_product = sum(x * y for x, y in zip(vector1_list, vector2_list))
            except ValueError as e:
                dot_product = "Error: One of the inputs is not a vector"
                raise e

            new_record = copy.deepcopy(record)
            new_record[self.output] = dot_product
            yield new_record


dispatch(DotProductCommand, sys.argv, sys.stdin, sys.stdout, __name__)
