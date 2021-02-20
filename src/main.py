import asyncio
import csv
import logging
import os
import sys
import threading
import tkinter as tk
from typing import List, Dict, Tuple
from PIL import Image
from src.core.log_handler import LogHandler
from src.core.util import Utils
from src.google_drive.file_manage import File_manage

HOME = Utils.get_project_root()
SUPPORTED_FORMATS = ['.png', '.jpg', '.tif', '.tiff', '.bmp', '.jpeg', '.gif']
TARGET_FORMAT = '.png'
DEFAULT_WIDTH = 842
DEFAULT_HEIGHT = 595
LOGS_FOLDER = os.path.join(Utils.get_project_root(), 'logs')
RAW_FOLDER = os.path.join(Utils.get_project_root(), 'img_raw')
OUTPUT_CSV = os.path.join(Utils.get_project_root(), 'processed.csv')

logger: logging.Logger


class Test_GUI:
    csv_detail: Dict[str, List[Tuple[int, int, int, int]]]
    rectangles: List[Tuple[int, int, int, int]] = []
    files: List[str]
    counter = 0
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

    @staticmethod
    def _exception_hook(exctype, exc, tb) -> None:
        logger.error("An unhandled exception occurred.", exc_info=(exctype, exc, tb))

    @staticmethod
    def init_logger() -> logging.Logger:
        sys.excepthook = Test_GUI._exception_hook
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
            im = Image.open(file)
            im.save(new_file)
            Utils.os_try_catch(lambda: os.remove(file))
            return new_file
        return None

    @staticmethod
    def to_correct_size(file: str, target_width: int, target_height: int) -> str or None:
        png_file = Test_GUI.to_png(file)
        if png_file is None:
            return None
        im = Image.open(png_file)
        width, height = im.size
        if (width, height) != (target_width, target_height):
            im = im.resize((target_width, target_height))
            Utils.os_try_catch(lambda: os.remove(png_file))
            im.save(png_file)
        return png_file

    @staticmethod
    def image_file_load(path: str) -> List[str]:
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        files = [Test_GUI.to_correct_size(f, DEFAULT_WIDTH, DEFAULT_HEIGHT) for f in files]
        return [f for f in files if f is not None]

    @staticmethod
    def read_csv(file: str) -> Dict[str, List[Tuple[int, int, int, int]]]:
        result = {}
        try:
            logger.info(f'reading detail from file {file}')
            with open(file, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=',')
                for row in csv_reader:
                    if row['name'] not in result:
                        result[row['name']] = []
                    result[row['name']].append((int(row['x1']), int(row['y1']), int(row['x2']), int(row['y2'])))
        except IOError:
            pass
        return result

    @staticmethod
    def write_csv(file: str, csv_detail: Dict[str, List[Tuple[int, int, int, int]]]) -> bool:
        rows: List[Dict[str, str]] = []
        for k, v in csv_detail.items():
            for pos in v:
                rows.append({'name': k, 'x1': str(pos[0]), 'y1': str(pos[1]), 'x2': str(pos[2]), 'y2': str(pos[3])})
        try:
            with open(file, 'w', newline='') as csv_file:
                field_names = ['name', 'x1', 'y1', 'x2', 'y2']
                csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
                csv_writer.writeheader()
                for row in rows:
                    csv_writer.writerow(row)
        except IOError:
            return False
        else:
            return True

    def submit(self, file):
        file_name = os.path.basename(file)
        self.csv_detail[file_name] = self.rectangles
        Test_GUI.write_csv(OUTPUT_CSV, self.csv_detail)
        self.counter += 1
        if self.counter < len(self.files):
            self.reset()
            new_file = self.files[self.counter]
            self.test_img = tk.PhotoImage(file=new_file)
            self.test_area.itemconfig(self.image, image=self.test_img)
            self.ok_button.configure(text='OK', command=lambda: self.submit(new_file))
            self.title.configure(text=os.path.basename(
                self.files[self.counter]) + ' (Left-click to draw a box, Right-click to clear, okay to submit)')

        else:
            popup = tk.Tk()
            popup.title('Test Finish')
            tk.Label(popup, text='You finished the Turing Test').pack(side=tk.TOP, anchor=tk.CENTER)
            tk.Button(popup, text='Exit', command=lambda: popup.destroy()).pack(side=tk.BOTTOM, anchor=tk.CENTER)
            popup.mainloop()

    def reset(self):
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

    def close_program(self):
        self.root.destroy()
        new_loop.stop()

    async def main(self):

        self.csv_detail = Test_GUI.read_csv(OUTPUT_CSV)
        self.files = self.image_file_load(RAW_FOLDER)
        self.counter = 0

        self.root = tk.Tk()
        self.root.title('AI Trainer')
        self.root.geometry(str(DEFAULT_WIDTH + 30) + 'x' + str(DEFAULT_HEIGHT + 50))
        self.root.protocol("WM_DELETE_WINDOW", self.close_program)

        self.title = tk.Label(self.root, text=os.path.basename(
            self.files[self.counter]) + ' (Left-click to draw a box, Right-click to clear, okay to submit)')
        self.title.pack(side=tk.TOP)

        self.test_area = tk.Canvas(self.root, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
        self.test_area.bind('<Button-1>', lambda event: self.start_rectangle(event))
        self.test_area.bind('<B1-Motion>', lambda event: self.draw_rectangle(event))
        self.test_area.bind('<ButtonRelease-1>', lambda event: self.add_rectangle_to_list())
        self.test_area.bind('<Button-3>', lambda event: self.reset())
        self.test_area.pack(side=tk.TOP, anchor=tk.CENTER)

        file = self.files[self.counter]
        self.test_img = tk.PhotoImage(file=file)
        self.image = self.test_area.create_image(1, 1, anchor=tk.NW, image=self.test_img)

        self.ok_button = tk.Button(self.root, text='OK', command=lambda: self.submit(file))
        self.ok_button.pack(side=tk.RIGHT, anchor=tk.W)

        # replace root.mainloop()
        while True:
            self.root.update()
            await asyncio.sleep(0)

if __name__ == '__main__':
    logger = Test_GUI.init_logger()
    test_gui = Test_GUI()
    manager = File_manage()
    title = manager.search('Raw Images')
    title = title[0]
    tasks = [asyncio.ensure_future(manager.download(None,title)), asyncio.ensure_future(test_gui.main())]
    new_loop = asyncio.get_event_loop()
    new_loop.run_until_complete(asyncio.wait(tasks))
