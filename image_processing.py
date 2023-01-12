from __future__ import print_function
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image
from io import BytesIO
import json

from controls import receipt_access, receipt_folder_id


def get_service(api_name='drive', api_version='v3', scopes='https://www.googleapis.com/auth/drive'):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    service_account_info = json.loads(receipt_access)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    scoped_credentials = credentials.with_scopes(scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=scoped_credentials)

    return service


def upload(file, file_name):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    # Define the auth scopes to request.
    scopes = ['https://www.googleapis.com/auth/drive']
    try:

        file_metadata = {
            # name of file to be uploaded
            'name': file_name,

            # folder to which file is uploaded
            # I'm too lazy to make it dynamic so if you share it a new folder
            # list the files and choose change this to that folder id
            'parents': [receipt_folder_id]
        }

        # Authenticate and construct service.
        service = get_service(
            api_name='drive',
            api_version='v3',
            scopes=scopes)

        # Call the Drive v3 API
        media = MediaIoBaseUpload(file, mimetype='image/png', resumable=True)
        fileCreate = service.files().create(body=file_metadata, media_body=media)
        fileCreateExecution = fileCreate.execute()
        fileID = fileCreateExecution['id']

        return fileID
        # list_files(key_file_location)

    except HttpError as error:
        print(f'An error occurred: {error}')


# Use only to clear files in root that cannot be manually deleted elsewhere
def purge(key_file_location, scope='https://www.googleapis.com/auth/drive'):

    try:
        # Authenticate and construct service.
        service = get_service(
            api_name='drive',
            api_version='v3',
            scopes=[scope],
            )

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()

        items = results.get('files', [])

        if not items:
            print('No files found.')
            return

        print('==deleting files==:')
        for item in items:
            try:
                service.files().delete(fileId=item['id']).execute()
                print("{} ({}) deleted successfully".format(item['name'], item['id']))
            except Exception as exc:
                print("Could not delete file: {} ({})".format(item['name'], item['id']))

    except HttpError as error:
        print(f'An error occurred: {error}')


def compress_file(file):
    """
    :param file: receipt (FileStorage object)
    :return: IO stream of compressed image as BytesIO object
    """

    # change file to bytes
    image_bytes = BytesIO(file.stream.read())
    # make PIL image object
    img = Image.open(image_bytes)
    # convert to black and white
    img = img.convert('1')

    # compress pixel size
    pixels = img.size[0] * img.size[1]
    if pixels > 921600:
        factor = 921600/pixels
        img = img.resize((round(img.size[0]*factor), round(img.size[1]*factor)))

    image_stream = BytesIO()
    img.save(image_stream, format='PNG')
    return image_stream


def list_files(key_file_location):
    """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """

    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/drive.metadata.readonly'

    try:
        # Authenticate and construct service.
        service = get_service(
            api_name='drive',
            api_version='v3',
            scopes=[scope])
        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    # this will delete everything, use at your own risk
    # purge(key_file_location='secret_data_lol.txt')
    list_files(key_file_location='secret_data_lol.txt')
