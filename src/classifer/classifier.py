import os

import torch
import torchvision
import torchvision.transforms as transforms

from classifer.dataset import FloorPlanDataset
from core.util import Utils

RESOURCE_FOLDER = os.path.join(Utils.get_project_root(), 'resource')
RAW_FOLDER = os.path.join(Utils.get_project_root(), 'img_raw')

if __name__ == '__main__':
    # [0.5,0.5,0.5] for RGB, [0.5] for Grayscale
    transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize([0.5], [0.5])])

    floorPlanSet = FloorPlanDataset(os.path.join(RESOURCE_FOLDER, 'trained.csv'), RAW_FOLDER, transform=transform)
    floorPlanLoader = torch.utils.data.DataLoader(floorPlanSet, batch_size=2,
                                                  shuffle=True, num_workers=2)

    trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                            download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=4,
                                              shuffle=True, num_workers=2)

    testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                           download=True, transform=transform)
    testloader = torch.utils.data.DataLoader(testset, batch_size=4,
                                             shuffle=False, num_workers=2)

    classes = ('plane', 'car', 'bird', 'cat',
               'deer', 'dog', 'frog', 'horse', 'ship', 'truck')
