import logging
from googleapiclient.errors import HttpError
from create_instance import create_instance

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

SOURCE_FOLDER_ID = "1saTWxTSFbtkFEAbeYPsuQCNaH_AkZq1v"
DESTINATION_FOLDER_ID = "1xGa0CusuRr_7Ta7Et6qLGCV-0LTZUtq5"
# DESTINATION_FOLDER_ID = "15NjBZwVZKbFbJQ-5zTJ-VYHnCB_SLsy7"
FOLDER_TYPE = "application/vnd.google-apps.folder"
source_drive = create_instance("source")
destination_drive = create_instance("destination")
IGNORED_IDS = ["1kmvqVAcs5Hsl4NtUeYtB2M_2qylJAcZs", "1Oyaga3x6rZgUVKHeOyt1FR-XkWJY4A_2"]

def log_error(error_message):
    logging.error(error_message)

def copy_file(file_id, name, destination_folder_id):
    new_file = {
        "title": name,
        "name": name,
        "parents": [destination_folder_id]
    }
    try:
        destination_drive.files().copy(fileId=file_id, body=new_file).execute()
    except HttpError as e:
        log_error(f"An error occurred: {e}\n"
                  f"File ID: {file_id}\n"
                  f"File Name: {name}\n"
                  f"Destination Folder ID: {destination_folder_id}\n")


def backup(source_folder_id: str, destination_folder_id: str):
    page_token = None
    while True:
        response = source_drive.files().list(
            q=f"'{source_folder_id}' in parents and trashed=false",
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType, parents)",
            pageToken=page_token
        ).execute()
        for file in response.get("files", []):
            if file.get("id") in IGNORED_IDS:
                continue
            if file.get("mimeType") == FOLDER_TYPE:
                new_folder = {
                    "name": file.get("name"),
                    "parents": [destination_folder_id],
                    "mimeType": FOLDER_TYPE
                }
                try:
                    new_folder = destination_drive.files().create(body=new_folder).execute()
                except Exception as e:
                    log_error(f"An error occurred: {e}")
                backup(file.get("id"), new_folder.get("id"))
            else:
                new_file = {
                    "title": file.get("name"),
                    "name": file.get("name"),
                    "parents": [destination_folder_id]
                }
                try:
                    print(file.get("name"))
                    destination_drive.files().copy(fileId=file.get("id"), body=new_file).execute()
                except Exception as e:
                    log_error(f"An error occurred: {e}\n"
                              f"File ID: {file.get('id')}\n"
                              f"File Name: {file.get('name')}"
                              f"Destination Folder ID: {destination_folder_id}\n")


        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break

if __name__ == "__main__":
   backup(source_folder_id=SOURCE_FOLDER_ID, destination_folder_id=DESTINATION_FOLDER_ID)
