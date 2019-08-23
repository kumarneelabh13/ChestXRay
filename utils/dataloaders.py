# -*- coding: utf-8 -*-
"""dataloaders.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j1Oz06lzCiDwbKyDSYQVxM1JGSoq5HcQ
"""

import os
import torch
import numpy as np
import pandas as pd
from PIL import Image
from skimage.transform import resize

import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader

def global_contrast_normalization(x: torch.tensor, scale='l2'):
    """
    Apply global contrast normalization to tensor, i.e. subtract mean across features (pixels) and normalize by scale,
    which is either the standard deviation, L1- or L2-norm across features (pixels).
    Note this is a *per sample* normalization globally across features (and not across the dataset).
    """

    assert scale in ('l1', 'l2')

    n_features = int(np.prod(x.shape))

    mean = torch.mean(x)  # mean over all features (pixels) per sample
    x -= mean

    if scale == 'l1':
        x_scale = torch.mean(torch.abs(x))

    if scale == 'l2':
        x_scale = torch.sqrt(torch.sum(x ** 2)) / n_features

    x /= x_scale

    return x

min_max = [-8.2690, 6.3035]

class ChestXRayDataset(Dataset):
    """Face Landmarks dataset."""

    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.xray_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.xray_frame)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir,
                                self.xray_frame['Image Index'][idx])
        
        img = Image.open(img_name)
        label = 0 if self.xray_frame['Finding Labels'][idx] == 'No Finding' else 1

        if self.transform:
            img = self.transform(img)

        return img, label, idx

transform = transforms.Compose([transforms.Lambda(lambda x: x.resize((224, 224))),
                                transforms.Grayscale(),
                                transforms.RandomHorizontalFlip(p=0.5),
                                transforms.RandomAffine(degrees=5, translate=None, scale=None, 
                                                        shear=5, resample=False, fillcolor=0),
                                transforms.ToTensor(),
                                transforms.Lambda(lambda x: global_contrast_normalization(x, scale='l1')),
                                transforms.Normalize([min_max[0]],
                                                     [min_max[1] - min_max[0]])])

'''trainset = ChestXRayDataset(csv_file='data/train.csv',
                                           root_dir='data/images', transform=transform)

valset = ChestXRayDataset(csv_file='data/val.csv',
                                           root_dir='data/images', transform=transform)

testset = ChestXRayDataset(csv_file='data/test.csv',
                                           root_dir='data/images', transform=transform)'''

'''microtrainset = ChestXRayDataset(csv_file='data/microtrain.csv',
                                           root_dir='data/images', transform=transform)

microvalset = ChestXRayDataset(csv_file='data/microval.csv',
                                           root_dir='data/images', transform=transform)

microtestset = ChestXRayDataset(csv_file='data/microtest.csv',
                                           root_dir='data/images', transform=transform)'''

def get_dataset(dataset='cleantrain'):
    return ChestXRayDataset(csv_file='data/'+dataset+'.csv', 
                            root_dir='data/images', transform=transform)
                           
    
def get_dataloader(dataset='clean', set_='train', batch_size=4, num_workers=4):
    if set_ != 'train':
        dataset = 'clean'
    dataset = get_dataset(dataset=dataset+set_)
    dataloader = DataLoader(dataset, batch_size=batch_size,
                                shuffle=True, num_workers=num_workers)
    
    return dataloader

