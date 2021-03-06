import numpy as np
import os
import torch
from torch.utils.data.dataloader import DataLoader
from torch.utils.data import Dataset


class StandardScaler:
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def transform(self, data):
        return (data - self.mean) / self.std

    def inverse_transform(self, data):
        return (data * self.std) + self.mean


class DCRNNDataset(Dataset):
    def __init__(self, inputs, targets):
        self.inputs = inputs
        self.targets = targets

    def __getitem__(self, item):
        return torch.cat([torch.FloatTensor(self.inputs[item]), torch.FloatTensor(self.targets[item])], 0), torch.FloatTensor(self.targets[item])[:, :, 0].squeeze()

    def __len__(self):
        return len(self.inputs)


def load_dataset(args):
    data = {}
    loader = {}
    phases = ['train', 'val', 'test']
    dataset_dir = args['data_dir']
    for phase in phases:
        cat_data = np.load(os.path.join(dataset_dir, phase + '.npz'))
        data['x_' + phase] = cat_data['x']
        data['y_' + phase] = cat_data['y']
    scaler = StandardScaler(mean=data['x_train'][..., 0].mean(),
                            std=data['x_train'][..., 0].std())
    for phase in phases:
        data['x_' + phase][..., 0] = scaler.transform(data['x_' + phase][..., 0])
        data['y_' + phase][..., 0] = scaler.transform(data['y_' + phase][..., 0])
    loader['scaler'] = scaler
    for phase in phases:
        print(data['x_' + phase].shape)
        loader[phase] = DataLoader(DCRNNDataset(data['x_' + phase], data['y_' + phase]), shuffle=True, drop_last=True, batch_size=args['batch_size'])
    return loader, scaler
