#Done By Dacorie Smith

import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

class AzureBlobUploader:
    def __init__(self, connection_string, container_name):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.get_or_create_container()

    def get_or_create_container(self):
        """Get or create a blob container in Azure."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.get_container_properties()
        except Exception:
            # If container does not exist, create it
            container_client = self.blob_service_client.create_container(self.container_name)
        return container_client

    def upload_file_to_blob(self, file_path, blob_name):
        """Uploads a file from local storage to Azure Blob Storage."""
        blob_client = self.container_client.get_blob_client(blob_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"Uploaded: {blob_name}")

    def upload_folder_to_blob(self, folder_path):
        """Upload all files from a local folder to Azure Blob Storage."""
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                blob_name = os.path.relpath(file_path, folder_path).replace("\\", "/")
                self.upload_file_to_blob(file_path, blob_name)


def main():
    # Azure storage account connection string
    connection_string = ""

    # Name of the blob container
    container_name = "sentienialanalyzecsv"

    # Local folder path to upload
    local_folder_path = "data/"

    # Initialize the AzureBlobUploader and upload the files
    blob_uploader = AzureBlobUploader(connection_string, container_name)
    blob_uploader.upload_folder_to_blob(local_folder_path)


if __name__ == "__main__":
    main()
