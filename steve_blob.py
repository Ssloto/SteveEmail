from azure.storage.blob import BlobClient
from tempfile import NamedTemporaryFile

class SteveBlob():
    def __init__(self, account_name, container_name, blob_name, credential):
        self.client = BlobClient(account_url="https://{}.blob.core.windows.net/".format(account_name), 
                                 container_name=container_name, 
                                 blob_name=blob_name, 
                                 snapshot=None, 
                                 credential=credential)


    def read_blob_to_text(self):
        return self.client.download_blob().readall()


    def write_blob(self, contents, overwrite=True):
        # w+b for reading AND writing
        with NamedTemporaryFile('w+b') as outf:
            # decode here to ensure we're writing UTF-8!
            outf.write(contents.encode("utf-8"))
            # go back to the beginning?
            outf.seek(0)
            # give file to client for upload!
            self.client.upload_blob(outf, overwrite=True)