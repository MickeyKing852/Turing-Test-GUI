import io
import logging
import os
import pickle
import time
import uuid
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, HttpRequest

from src.core.util import Utils
from src.google_drive.corpora import Corpora
from src.google_drive.file import File
from src.google_drive.permission import PermissionList, Permission, PermissionRole

# For required scope, refer to Authorization section of each page:
# e.g. https://developers.google.com/drive/api/v3/reference/files/create#auth
# If scope is changed, delete token.pickle before re-running the application
SCOPES = ['https://www.googleapis.com/auth/drive.file']

logger = logging.getLogger(__name__)


class Drive:
    _creds: Credentials = None
    _service: Resource = None
    upload_status: Dict[uuid.UUID, bool] = {}

    def __new__(cls):  # __new__ always a classmethod
        if Drive._service is None:
            Drive._service = Drive._get_service()
        return super(Drive, cls).__new__(cls)

    @staticmethod
    def _get_credential(credentials_path: str = None) -> Credentials:
        if Drive._creds is None:
            if credentials_path is None:
                credentials_path = os.path.join(Utils.get_project_root(), 'credentials.json')
            creds: Credentials or None = None
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('../../token.pickle'):
                with open('../../token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('../../token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            Drive._creds = creds
        return Drive._creds

    @staticmethod
    def _get_service() -> Resource:
        if Drive._service is None:
            Drive._service = build('drive', 'v3', credentials=Drive._get_credential())
        return Drive._service

    @staticmethod
    def file_info(file_id: str) -> File:
        d: Dict[str, str] = Drive._get_service().files().get(fileId=file_id).execute()
        return File(**d)

    @staticmethod
    def list(file_id: str, max_count=10) -> List[File]:
        folder_info: File = Drive.file_info(file_id)
        logger.info(f'Fetching file for {folder_info}')
        page_token: str or None = None
        i = 0
        files = []
        while (i == 0 or page_token is not None) and len(files) < max_count:
            query = f"'{file_id}' in parents"
            response: Dict[str, object] = Drive._get_service().files().list(corpora=Corpora.USER.value, q=query,
                                                                            pageToken=page_token).execute()
            response_files = [File(**file_dict) for file_dict in response.get('files', [])]
            files.extend(response_files[0:max_count - len(files)])
            page_token = response.get('nextPageToken', None)
            i += 1
        logger.info(f'{len(files)} files fetched for {folder_info}')
        return files

    @staticmethod
    def download(file_id: str, target_folder: str, override=False) -> None:
        drive_file: File = Drive.file_info(file_id)
        file = os.path.join(target_folder, drive_file.name)
        if os.path.isfile(file) and not override:
            logger.info(f'Downloading skipped, {file} already exists')
            return
        logger.info(f'Downloading {drive_file} to {file}')
        request = Drive._get_service().files().get_media(fileId=file_id)
        handle = io.FileIO(os.path.join(target_folder, drive_file.name), 'wb')
        downloader = MediaIoBaseDownload(handle, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info(f'Download {int(status.progress() * 100)}%.')
        logger.info(f'Download done for {drive_file}')

    @staticmethod
    def upload_single(file_id: str, source_file: str) -> None:
        drive_file: File = Drive.file_info(file_id)
        if not os.path.isfile(source_file):
            logger.error(f'Uploading failed: {source_file} not exist')
            return
        logger.info(f'Uploading {source_file} to {drive_file}')
        metadata = {'name': os.path.basename(source_file), 'parents': [file_id]}
        media = MediaFileUpload(source_file)
        d = Drive._get_service().files().create(body=metadata, media_body=media).execute()
        logger.info(f'Uploading done for {File(**d)}')

    @staticmethod
    def rename(file_id: str, new_name: str) -> None:
        drive_file: File = Drive.file_info(file_id)
        logger.info(f'Renaming file for {drive_file} to {new_name}')
        d = Drive._get_service().files().update(fileId=file_id, body={'name': new_name}).execute()
        logger.info(f'Renamed file to {File(**d)}')

    @staticmethod
    def permission_info(file_id: str) -> PermissionList:
        d: Dict[str, object] = Drive._get_service().permissions().list(fileId=file_id).execute()
        return PermissionList(**d)

    # As mentioned in https://support.google.com/drive/answer/2494892?hl=en
    # Permission update can only be done for google files or folders, pdf and images won't work
    # e.g. p = Permission(PermissionKind.PERMISSION.value, UserId.HOWOON.value, Corpora.USER.value, PermissionRole.OWNER.value)
    #      Drive.permission_update('1uSPzAv3m2lyIza15gWBE41rMsbkuY29QlekQduXLzjI', [p])
    @staticmethod
    def permission_update(file_id: str, permission_list: List[Permission] or PermissionList = None) -> None:
        permissions: List[Permission] = []
        if type(permission_list) is PermissionList:
            permissions = permission_list.permissions
        elif type(permission_list) is list:
            permissions = permission_list
        batches: List[HttpRequest] = []
        for permission in permissions:
            body = {'role': permission.role.value}
            is_transfer = permission.role is PermissionRole.OWNER
            batches.append(Drive._get_service().permissions().update(fileId=file_id, permissionId=permission.id,
                                                                     transferOwnership=is_transfer, body=body))
        Drive._batch(batches)

    # Google API does not support batch upload at the moment
    # @staticmethod
    # def upload_batch(file_id: str, source_files: List[str]) -> None:
    #     drive_file: File = Drive.file_info(file_id)
    #     logger.info(f'Batch uploading {len(source_files)} files to {drive_file}')
    #     batches: List[HttpRequest] = []
    #     for source_file in source_files:
    #         if os.path.isfile(source_file):
    #             metadata = {'name': os.path.basename(source_file), 'parents': [file_id]}
    #             media = MediaFileUpload(source_file)
    #             batches.append(Drive._get_service().files().create(body=metadata, media_body=media))
    #     Drive._batch(batches)

    @staticmethod
    def _batch(batch_list: List[HttpRequest]) -> List[uuid.UUID]:
        batch_max = 1000  # internal limit for Google Drive batch upload
        batches = [batch_list[i: i + batch_max] for i in range(0, len(batch_list), batch_max)]

        logger.info(f'Making {len(batch_list)} operations into {len(batches)} batch(es)')

        batch_ids: List[uuid.UUID] = []
        for batch_ops in batches:
            batch_id = uuid.uuid4()
            Drive.upload_status[batch_id] = False
            batch_ids.append(batch_id)

            def callback(request_id, response, exception):
                if exception:
                    logger.error(exception)
                else:
                    logger.info(f'Done for request_id={request_id}, response={response}')
                    Drive.upload_status[batch_id] = True

            batch = Drive._get_service().new_batch_http_request(callback=callback)
            for op in batch_ops:
                batch.add(op)
            batch.execute()
            logger.info(f'Batch {batch_id} started execution')
        for batch_id in batch_ids:
            while not Drive.upload_status[batch_id]:
                logger.info(f'Waiting for batch {batch_id} to be done')
                time.sleep(5)
        return batch_ids
