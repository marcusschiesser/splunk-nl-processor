import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option

# XXX: We're not using the Huggingface Datasets API because it's not working with Splunk's Python version (it's missing the `mmap` module)
import requests
import parquet
from io import BytesIO
from splunklib import client
from passwords import decode_password


@Configuration()
class HfDatasetCommand(GeneratingCommand):
    hf_api_token = None
    dataset = Option(name="dataset", require=True)
    split = Option(name="split", default="train", require=False)

    def read_parquet(self, url):
        """Read the parquet file from the given url"""
        response = requests.get(url)
        file_stream = BytesIO(response.content)
        return parquet.DictReader(file_stream)

    def get_dataset(self):
        """Calls the Huggingface Datasets API"""
        headers = {"Authorization": f"Bearer {self.hf_api_token}"}
        API_URL = (
            f"https://datasets-server.huggingface.co/parquet?dataset={self.dataset}"
        )
        response = requests.get(API_URL, headers=headers)
        json = response.json()
        if "parquet_files" not in json:
            raise ValueError(f"Dataset {self.dataset} does not exist")
        return json["parquet_files"]

    def generate(self):
        session_key = self.metadata.searchinfo.session_key
        app_name = self.metadata.searchinfo.app
        service = client.Service(token=session_key, app=app_name)
        self.hf_api_token = decode_password(service, "hf_api_token")

        files = self.get_dataset()
        self.logger.info(
            f'msg="Successfully called HF dataset API" dataset="{self.dataset}"'
        )
        # find first file with the matching split
        try:
            file = next(filter(lambda x: x["split"] == self.split, files))
        except StopIteration as e:
            raise ValueError(f"Split {self.split} doesn't exist in the dataset", e)
        url = file["url"]
        filename = file["filename"]
        self.logger.info(
            f'msg="Start downloading parquet file" dataset="{self.dataset}" url="{url}" filename="{filename}"'
        )
        for row in self.read_parquet(url):
            yield row


dispatch(HfDatasetCommand, sys.argv, sys.stdin, sys.stdout, __name__)
