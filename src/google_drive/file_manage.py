from typing import List
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from src.core.util import Utils
import asyncio
import os
import logging

HOME = Utils.get_project_root()


class File_manage():

    def __init__(self):

        self.log_setup()
        self.authencation()

    def log_setup(self):
        log_format = '%(asctime)s -- %(levelname)s -- %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt='%d/%m/%Y-%H:%M')

    def authencation(self):
        # auth section
        GAUTH = GoogleAuth()
        GAUTH.LocalWebserverAuth()
        self.DRIVE = GoogleDrive(GAUTH)

    def search(self, title: str) -> List[str]:
        try:
            query_format = 'trashed = false and title contains "{file_title}" '
            query = query_format.format(file_title=title)
            logging.info('Start to searching target file')
            file_list = self.DRIVE.ListFile({'q': query}).GetList()
            logging.info('return data')
            return [file['id'] for file in file_list]

        except Exception as e:
            return [f'{logging.error(e)}']

    def upload(self, file_path: str, file_title: str, folder_id: str) -> str:
        try:
            upload = self.DRIVE.CreateFile({'title': file_title, 'parents': [{'id': folder_id}]})
            upload.SetContentFile(file_path)
            logging.info(
                f"start to upload file with parent id {folder_id}, title {file_title} and local path {file_path}")
            upload.Upload()
            logging.info(f'{file_title} upload successfully')
            return f'{file_title} upload successfully'

        except Exception as e:

            return f'{logging.error(e)}'

    async def download(self, file_id, folder_id) -> str:
        try:
            query_format = 'trashed = false and "{id}" in parents'
            if os.path.exists(f'{HOME}/img_raw'):
                pass
            else:
                os.mkdir(f'{HOME}/img_raw')

            logging.info(f'try to get file id by the query')
            if folder_id is not None:
                query = query_format.format(id=folder_id)
                file_list = self.DRIVE.ListFile({'q': query}).GetList()

            elif file_id is not None:
                query = query_format.format(id=file_id)
                file_list = self.DRIVE.ListFile({'q': query}).GetList()

            else:
                e = 'file_id or/and folder_id incorrect'
                raise RuntimeError

            for file in file_list:
                download = self.DRIVE.CreateFile({'id': file['id']})
                logging.info(
                    f"start to download file with file id {file['id']}, title {file['title']} and parent id {folder_id}")
                content = download.GetContentFile(file['title'])
                os.replace(file['title'], f"{HOME}/img_raw/{file['title']}")
                await asyncio.sleep(5)

        except RuntimeError as e:
            return f'{logging.warning(e)}'

        except Exception as e:
            return f'{logging.warning(e)}'
