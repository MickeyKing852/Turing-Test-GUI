import os

import pandas as pd
from PIL import Image
from torch.utils.data import Dataset

TRAIN_RATIO = 0.8  # 80% Train, 20% Test


class FloorPlanDataset(Dataset):
    def __init__(self, csv_file, root_dir, train=True, transform=None):
        self.annotations = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.train = train
        self.transform = transform

    def __len__(self):
        ratio = TRAIN_RATIO if self.train is True else 1 - TRAIN_RATIO
        return round(ratio * len(self.annotations))

    def __getitem__(self, index):
        idx = index if self.train is True else index + len(self)
        img_name = os.path.join(self.root_dir, self.annotations['name'][index])
        image = Image.open(img_name).convert('L')
        return self.transform(image) if self.transform else image, self.annotations['room'][index].item()

    # landmarks = self.annotations.iloc[index, 1:]
    # landmarks = np.asarray(landmarks)
    # landmarks = landmarks.astype('float').reshape(-1, 2)
    # arr = np.array(image)
    # sample = {'image': image, 'landmarks': landmarks}
    # result = image, np.asarray([self.annotations['room'][index]])
