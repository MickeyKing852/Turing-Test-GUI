import os

import numpy as np
import pandas as pd
from PIL import Image

from src.core.util import Utils
from src.google_drive.drive import Drive

DEFAULT_WIDTH = 842
DEFAULT_HEIGHT = 595
NEW_WIDTH = 224
NEW_HEIGHT = 224
RAW_FOLDER = os.path.join(Utils.get_project_root(), 'img_raw')
PROCESSED_FOLDER = os.path.join(Utils.get_project_root(), 'img_processed')
RESOURCE_FOLDER = os.path.join(Utils.get_project_root(), 'resource')
FLOOR_PLAN_IMAGES_FOLDER_ID = '1u1QpBbcumSra8StCwtaOZTdFDdtpXUU3'
RAW_IMAGES_FOLDER_ID = '1Of2lHAj2MO8laNdzE5qVM1oGlpfXRnoU'
PROCESSED_IMAGES_FOLDER_ID = '19BjKK-aPlt-R8NMYTNhSIQMZkVeg-Pni'


def create_neg(p: np.ndarray, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT) -> np.ndarray:
    n = np.array([min(p[0], p[2]), min(p[1], p[3]), max(p[0], p[2]), max(p[1], p[3])])
    if n[0] < width / 2:
        n[0] = min(n[0] + int((n[2] - n[0]) / 2), width)
        n[2] = min(n[2] + int((n[2] - n[0]) / 2), width)
    else:
        n[0] = max(n[0] - int((n[2] - n[0]) / 2), 0)
        n[2] = max(n[2] - int((n[2] - n[0]) / 2), 0)
    if n[1] < height / 2:
        n[1] = min(n[1] + int((n[3] - n[1]) / 2), height)
        n[3] = min(n[3] + int((n[3] - n[1]) / 2), height)
    else:
        n[1] = max(n[1] - int((n[3] - n[1]) / 2), 0)
        n[3] = max(n[3] - int((n[3] - n[1]) / 2), 0)
    return n


if __name__ == '__main__':
    file_list_cache = pd.read_csv(os.path.join(RESOURCE_FOLDER, 'file_list_cache.csv'))
    file_list_cache.set_index('name', inplace=True)

    processed_data = pd.read_csv(os.path.join(RESOURCE_FOLDER, 'processed.csv'))
    # processed_data = pd.read_csv(os.path.join(RESOURCE_FOLDER, 'processed_sample.csv'))
    file_names = pd.unique(processed_data.name)

    trained: pd.DataFrame
    try:
        trained = pd.read_csv(os.path.join(RESOURCE_FOLDER, 'trained_vgg16.csv'))
        # trained = pd.read_csv(os.path.join(RESOURCE_FOLDER, 'trained.csv'))
    except IOError:
        trained = pd.DataFrame(columns=['name', 'room'])
    trained.set_index('name', inplace=True)

    for file_name in file_names:
        # file_detail: pd.Series or None = None
        # name = file_name
        # for ext in ['.jpg', '.jpeg', '.png']:
        #     try:
        #         name = os.path.splitext(file_name)[0] + ext
        #         file_detail = file_list_cache.loc[name]
        #         break
        #     except KeyError:
        #         pass
        # Drive.download(file_detail.id, RAW_FOLDER, override=False)
        name = file_name
        file = os.path.join(RAW_FOLDER, name)
        im = Image.open(file).convert('L')
        data = processed_data[processed_data.name == file_name]
        counter = 1
        for loc in data.iloc[:, 1:].values:
            pos = np.array([min(loc[0], loc[2]), min(loc[1], loc[3]), max(loc[0], loc[2]), max(loc[1], loc[3])])
            neg = create_neg(pos)
            # im_pos = im.resize((DEFAULT_WIDTH, DEFAULT_HEIGHT)).crop(pos).resize((NEW_WIDTH, NEW_HEIGHT))
            im_pos = im.crop(pos).resize((NEW_WIDTH, NEW_HEIGHT))
            pos_filename = f'{os.path.splitext(name)[0]}_pos_{str(counter).zfill(2)}.png'
            im_pos.save(os.path.join(PROCESSED_FOLDER, pos_filename), "PNG")
            trained.loc[pos_filename] = 1
            # im_neg = im.resize((DEFAULT_WIDTH, DEFAULT_HEIGHT)).crop(neg).resize((NEW_WIDTH, NEW_HEIGHT))
            im_neg = im.crop(neg).resize((NEW_WIDTH, NEW_HEIGHT))
            neg_filename = f'{os.path.splitext(name)[0]}_neg_{str(counter).zfill(2)}.png'
            im_neg.save(os.path.join(PROCESSED_FOLDER, neg_filename), "PNG")
            trained.loc[neg_filename] = 0
            counter += 1
    trained.reset_index().to_csv(os.path.join(RESOURCE_FOLDER, 'trained_vgg16.csv'), index=False)
    # Drive.upload_single(FLOOR_PLAN_IMAGES_FOLDER_ID, os.path.join(RESOURCE_FOLDER, 'trained.csv'))
