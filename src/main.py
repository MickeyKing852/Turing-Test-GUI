import csv
import logging
import os
import sys
import tkinter as tk
from random import randint

import pandas as pd
from typing import List, Dict, Tuple

from PIL import Image

from src.core.log_handler import LogHandler
from src.core.util import Utils
from src.google_drive.drive import Drive
from src.google_drive.file import File

SUPPORTED_FORMATS = ['.png', '.jpg', '.tif', '.tiff', '.bmp', '.jpeg', '.gif']
TARGET_FORMAT = '.png'
DEFAULT_WIDTH = 842
DEFAULT_HEIGHT = 595
RESOURCE_FOLDER = os.path.join(Utils.get_project_root(), 'resource')
LOGS_FOLDER = os.path.join(Utils.get_project_root(), 'logs')
RAW_FOLDER = os.path.join(Utils.get_project_root(), 'img_raw')
OUTPUT_CSV = os.path.join(Utils.get_project_root(), 'processed.csv')
FLOOR_PLAN_IMAGES_FOLDER_ID = '1u1QpBbcumSra8StCwtaOZTdFDdtpXUU3'
RAW_IMAGES_FOLDER_ID = '1Of2lHAj2MO8laNdzE5qVM1oGlpfXRnoU'
PROCESSED_IMAGES_FOLDER_ID = '19BjKK-aPlt-R8NMYTNhSIQMZkVeg-Pni'

logger: logging.Logger


class Trainer:
    processed_data: pd.DataFrame = pd.DataFrame(columns=['name', 'x1', 'y1', 'x2', 'y2'])
    rectangles: List[Tuple[int, int, int, int]] = []
    file: str
    test_area: tk.Canvas
    p1: Tuple[int, int] or None = None
    p2: Tuple[int, int] or None = None
    selected_areas = []
    area = None
    ok_button = None
    data = {'result': [], 'img_info': []}
    image_map = {}
    image = None
    test_img = None  # tkinter requires image to be stored in local variable or else it will not work
    cache_list: List[File] = []

    @staticmethod
    def _exception_hook(exctype, exc, tb) -> None:
        logger.error("An unhandled exception occurred.", exc_info=(exctype, exc, tb))

    @staticmethod
    def init_logger() -> logging.Logger:
        sys.excepthook = Trainer._exception_hook
        formatter = logging.Formatter(
            '%(levelname)s [%(asctime)s] [%(module)s.%(funcName)s] %(message)s')
        handler = LogHandler(formatter, os.path.join(LOGS_FOLDER, 'test_gui.log'))
        logging.basicConfig(**{'level': logging.INFO, 'handlers': [handler]})
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
        return logging.getLogger()

    @staticmethod
    def to_png(file: str) -> str or None:
        file_name = os.path.basename(file).lower()
        extension_matched = [extension for extension in SUPPORTED_FORMATS if file_name.endswith(extension)]
        if len(extension_matched) > 0:
            if file_name.endswith(TARGET_FORMAT):
                return file
            new_file = os.path.join(os.path.dirname(file), file_name.replace(extension_matched[0], TARGET_FORMAT))
            im = Image.open(file).convert('L')
            im.save(new_file)
            Utils.os_try_catch(lambda: os.remove(file))
            return new_file
        return None

    @staticmethod
    def to_correct_size(file: str, target_width: int, target_height: int) -> str or None:
        png_file = Trainer.to_png(file)
        if png_file is None:
            return None
        im = Image.open(png_file).convert('L')
        width, height = im.size
        if (width, height) != (target_width, target_height):
            im = im.resize((target_width, target_height))
        Utils.os_try_catch(lambda: os.remove(png_file))
        im.save(png_file)
        return png_file

    @staticmethod
    def image_file_load(path: str) -> List[str]:
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        files = [Trainer.to_correct_size(f, DEFAULT_WIDTH, DEFAULT_HEIGHT) for f in files]
        return [f for f in files if f is not None]

    @staticmethod
    def write_csv(processed_data: pd.DataFrame, file: str) -> bool:
        processed_data.to_csv(file, index=False)
        Drive.upload_single(FLOOR_PLAN_IMAGES_FOLDER_ID, file)
        return True

    def submit(self, file: str) -> None:
        file_name = os.path.basename(file)
        for rect in self.rectangles:
            self.processed_data = self.processed_data.append({'name': file_name, 'x1': str(rect[0]), 'y1': str(rect[1]),
                                                              'x2': str(rect[2]), 'y2': str(rect[3])},
                                                             ignore_index=True)
        Trainer.write_csv(self.processed_data, os.path.join(RESOURCE_FOLDER, 'processed.csv'))
        Drive.upload_single(PROCESSED_IMAGES_FOLDER_ID, file)
        self.reset()
        new_file = self.get_next_image(RAW_IMAGES_FOLDER_ID, FLOOR_PLAN_IMAGES_FOLDER_ID, 'processed.csv')
        self.test_img = tk.PhotoImage(file=new_file)
        self.test_area.itemconfig(self.image, image=self.test_img)
        self.ok_button.configure(text='OK', command=lambda: self.submit(new_file))
        self.title.configure(text=f'{os.path.basename(self.file)} - (Hold left button and drag to draw a box, '
                                  f'right click to reset, okay to submit)')
        # else:
        #     popup = tk.Tk()
        #     popup.title('Test Finish')
        #     tk.Label(popup, text='You finished the Turing Test').pack(side=tk.TOP, anchor=tk.CENTER)
        #     tk.Button(popup, text='Exit', command=lambda: popup.destroy()).pack(side=tk.BOTTOM, anchor=tk.CENTER)
        #     popup.mainloop()

    def reset(self) -> None:
        self.rectangles = []
        self.p1 = None
        self.p2 = None
        for area in self.selected_areas:
            self.test_area.delete(area)
        if self.area is not None:
            self.test_area.delete(self.area)
        self.selected_areas = []

    def start_rectangle(self, event):
        self.p1 = event.x, event.y

    def draw_rectangle(self, event):
        self.p2 = event.x, event.y
        if self.p1 is not None and self.p2 is not None:
            if self.area is not None:
                self.test_area.delete(self.area)
            self.area = self.test_area.create_rectangle(self.p1, self.p2, outline='red', width=3)

    def add_rectangle_to_list(self):
        if self.p1 is not None and self.p2 is not None:
            self.rectangles.append((self.p1[0], self.p1[1], self.p2[0], self.p2[1]))
        if self.area is not None:
            self.selected_areas.append(self.area)
            self.area = None

    def get_next_image(self, folder_id: str, processed_file_folder_id: str, processed_file_name: str) -> str or None:
        cache_file = os.path.join(RESOURCE_FOLDER, 'file_list_cache.csv')
        self.processed_data = self.get_processed_names(processed_file_folder_id, processed_file_name)
        processed_names: List[str] = pd.unique(self.processed_data['name'])
        cache_list: List[File] = self.get_cache_files(folder_id, cache_file)
        unprocessed_names = [x for x in cache_list if x.name not in processed_names]
        next_image: File = unprocessed_names[randint(0, len(unprocessed_names) - 1)]
        logger.info(f'next image is {next_image}')
        Drive.download(next_image.id, RAW_FOLDER, override=True)
        image = Trainer.to_correct_size(os.path.join(RAW_FOLDER, next_image.name), DEFAULT_WIDTH, DEFAULT_HEIGHT)
        # image = Trainer.to_correct_size(os.path.join(RAW_FOLDER, 'mid_img26350.png'), DEFAULT_WIDTH, DEFAULT_HEIGHT)
        return image

    def get_cache_files(self, folder_id: str, cache_file: str) -> List[File]:
        if len(self.cache_list) == 0:
            data: pd.DataFrame
            try:
                data = pd.read_csv(cache_file)
                self.cache_list = [File(**item) for item in data.to_dict('records')]
            except IOError:
                logger.info(f'Cache not exist ({cache_file}), downloading from drive')
                self.cache_list = Drive.list(folder_id, max_count=sys.maxsize)
                data = pd.DataFrame([file.to_dict() for file in self.cache_list])
                data.to_csv(cache_file, index=False)
        return self.cache_list

    def get_processed_names(self, processed_file_folder_id: str, processed_file_name: str) -> pd.DataFrame:
        data: pd.DataFrame = self.processed_data
        if len(data) == 0:
            files: List[File] = Drive.list(processed_file_folder_id, max_count=sys.maxsize)
            processed_file = [file for file in files if file.name == processed_file_name]
            if len(processed_file) > 0:
                Drive.download(processed_file[0].id, RESOURCE_FOLDER, override=True)
                file_path = os.path.join(RESOURCE_FOLDER, processed_file[0].name)
                data = pd.read_csv(file_path)
        return data

    def main(self):
        self.file: str or None = self.get_next_image(RAW_IMAGES_FOLDER_ID, FLOOR_PLAN_IMAGES_FOLDER_ID, 'processed.csv')

        root = tk.Tk()
        root.title('Floor Plan AI Trainer')
        root.geometry(str(DEFAULT_WIDTH + 30) + 'x' + str(DEFAULT_HEIGHT + 50))

        self.title = tk.Label(root, text=f'{os.path.basename(self.file)} - (Hold left button and drag to draw a box, '
                                         f'right click to reset, okay to submit)')
        self.title.pack(side=tk.TOP)

        self.test_area = tk.Canvas(root, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
        self.test_area.bind('<Button-1>', lambda event: self.start_rectangle(event))
        self.test_area.bind('<B1-Motion>', lambda event: self.draw_rectangle(event))
        self.test_area.bind('<ButtonRelease-1>', lambda event: self.add_rectangle_to_list())
        self.test_area.bind('<Button-3>', lambda event: self.reset())
        self.test_area.pack(side=tk.TOP, anchor=tk.CENTER)

        self.test_img = tk.PhotoImage(file=self.file)
        self.image = self.test_area.create_image(1, 1, anchor=tk.NW, image=self.test_img)

        self.ok_button = tk.Button(root, text='OK', command=lambda: self.submit(self.file))
        self.ok_button.pack(side=tk.RIGHT, anchor=tk.W)

        root.mainloop()


if __name__ == '__main__':
    logger = Trainer.init_logger()
    trainer = Trainer()
    trainer.main()
