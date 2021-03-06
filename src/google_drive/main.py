import logging
import os
import shutil
import sys
import zipfile
from typing import List

from PIL import Image

from src.core.log_handler import LogHandler
from src.core.util import Utils
from src.google_drive.drive import Drive
from src.google_drive.file import File, MimeType

LOGS_FOLDER = os.path.join(Utils.get_project_root(), 'logs')
IMG_FOLDER = os.path.join(Utils.get_project_root(), 'img')
RAW_FOLDER = os.path.join(Utils.get_project_root(), 'img_raw')
FLOOR_PLAN_IMAGES_FOLDER_ID = '1u1QpBbcumSra8StCwtaOZTdFDdtpXUU3'
RAW_IMAGES_FOLDER_ID = '1Of2lHAj2MO8laNdzE5qVM1oGlpfXRnoU'
PROCESSED_IMAGES_FOLDER_ID = '19BjKK-aPlt-R8NMYTNhSIQMZkVeg-Pni'
SAMPLE_IMAGE = '1FSMo0L0rZRcRSNbPUeYDLXMhoGSMyXkL'

logger: logging.Logger


class DriveAccessor:
    @staticmethod
    def _exception_hook(exctype, exc, tb) -> None:
        logger.error("An unhandled exception occurred.", exc_info=(exctype, exc, tb))

    @staticmethod
    def init_logger() -> logging.Logger:
        sys.excepthook = DriveAccessor._exception_hook
        formatter = logging.Formatter(
            '%(levelname)s [%(asctime)s] [%(module)s.%(funcName)s] %(message)s')
        handler = LogHandler(formatter, os.path.join(LOGS_FOLDER, 'drive.log'))
        logging.basicConfig(**{'level': logging.INFO, 'handlers': [handler]})
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
        return logging.getLogger()

    @staticmethod
    def main():
        logger.info('==========================')
        logger.info('Program started')
        logger.info('==========================')
        files: List[File] = Drive.list(PROCESSED_IMAGES_FOLDER_ID, max_count=sys.maxsize)
        for file in files:
            Drive.download(file.id, RAW_FOLDER, override=False)
            f = os.path.join(RAW_FOLDER, file.name)
            im = Image.open(f).convert('L')
            im.save(f)
            Drive.upload_single(PROCESSED_IMAGES_FOLDER_ID, f)
        # logger.info(f'File details for Floor Plan Folder = {", ".join([str(x) for x in files])}')
        # file = Drive.file_info('1Z4vxJe39zUejiyB75MpqJLDrg1cP2M_5')
        # logger.info(f'File detail = {file}')
        # permission = Drive.permission_info('1Z4vxJe39zUejiyB75MpqJLDrg1cP2M_5')
        # logger.info(f'Permission detail = {permission}')

        # Drive.upload_single(PROCESSED_IMAGES_FOLDER_ID, os.path.join(Utils.get_project_root(), 'img', 'img10001.png'))
        # zip_files: List[File] = [x for x in files if x.mimeType is MimeType.ZIP and not x.name.startswith('Done_')]
        # download_folder = Utils.get_project_root()
        # for i in range(0, len(zip_files)):
        #     zip_file = zip_files[i]
        #     logger.info(f'Processing zip file {i + 1}/{len(zip_files)}: {zip_file.name}')
        #     zip_folder = os.path.join(download_folder, os.path.splitext(zip_file.name)[0])
        #     zip_file_path = os.path.join(download_folder, zip_file.name)
        #     Drive.download(zip_file.id, download_folder)
        #     if os.path.exists(zip_folder):
        #         logger.info(f'Unzip folder already exists ({zip_folder}), unzipping not done')
        #     else:
        #         logger.info(f'Extracting {zip_file.name} to {zip_folder}')
        #         Utils.os_try_catch(lambda: os.makedirs(zip_folder))
        #         with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        #             zip_ref.extractall(zip_folder)
        #     img_files = [os.path.join(zip_folder, f) for f in os.listdir(zip_folder) if
        #                  os.path.isfile(os.path.join(zip_folder, f))]
        #     for j in range(0, len(img_files)):
        #         logger.info(
        #             f'Processing zip file {i + 1}/{len(zip_files)}, file {j + 1}/{len(img_files)}: {img_files[j]}')
        #         Drive.upload_single(RAW_IMAGES_FOLDER_ID, os.path.join(zip_folder, img_files[j]))
        #     logger.info(f'Doing cleanup for {zip_file.name}')
        #     Utils.os_try_catch(lambda: shutil.rmtree(zip_folder))
        #     Utils.os_try_catch(lambda: os.remove(zip_file_path))
        #     Drive.rename(zip_file.id, 'Done_' + zip_file.name)
        #     logger.info(f'Processed zip file {i + 1}/{len(zip_files)}: {zip_file.name}')
        logger.info('Program done')


if __name__ == '__main__':
    logger = DriveAccessor.init_logger()
    DriveAccessor.main()
