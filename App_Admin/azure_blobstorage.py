from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient
import os
from datetime import date
 
# Configuration
TENANT_ID = "b2aa0d4b-c7bf-49f4-9539-6ff110ea720d"
CLIENT_ID = "4c676a8b-1afa-471f-b199-d643ba8e6fa4"
CLIENT_SECRET = "VsC8Q~kiRAD4iFnPHzffrpkhYIe32n_8SPlhyajV"
STORAGE_ACCOUNT_NAME = "neucodestoragedev"
FILE_SYSTEM_NAME = "neucode-container"
LOCAL_DIRECTORY = "D:/Projects/Neucode/Neucode Talent/NFS_360/reports"  #"<path-to-your-local-directory-containing-pdfs>"
current_date = date.today() #dd-mm-yyyy
formatted_date = current_date.strftime("%d-%m-%Y")
DESTINATION_PATH = "https://neucodestoragedev.blob.core.windows.net/neucode-container/outbound/report/{formatted_date}"  # e.g., "folder/subfolder"
 
# Authenticate with Azure AD
credentials = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
 
# Connect to Data Lake Storage
service_client = DataLakeServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", credential=credentials)
 
# Get a file system client
file_system_client = service_client.get_file_system_client(file_system=FILE_SYSTEM_NAME)
 
def upload_file_to_data_lake(local_file_path, destination_file_path):
    try:
        # Create a file client
        file_client = file_system_client.get_file_client(destination_file_path)
 
        # Upload file content
        with open(local_file_path, "rb") as file:
            file_client.upload_data(file, overwrite=True)
 
        print(f"Uploaded {local_file_path} to {destination_file_path}")
    except Exception as e:
        print(f"Failed to upload {local_file_path} to {destination_file_path}: {e}")
 
# Iterate through local directory and upload PDFs
for root, dirs, files in os.walk(LOCAL_DIRECTORY):
    for file in files:
        if file.endswith(".pdf"):
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, LOCAL_DIRECTORY)
            destination_file_path = os.path.join(DESTINATION_PATH, relative_path).replace("\\", "/")
 
            upload_file_to_data_lake(local_file_path, destination_file_path)