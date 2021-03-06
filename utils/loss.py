import torch.nn as nn
import numpy as np
import torch
from utils.util import convert_to_gpu


class MSELoss(nn.Module):
    def __init__(self):
        super(MSELoss, self).__init__()
        self.mse_loss = nn.MSELoss(reduction='sum')

    def forward(self, truth, predict):
        """
        Args:
            truth: tensor, (batch_size, predict_dim)
            predict: tenor, (batch_size, predict_dim)
        Returns:
            output: loss value
        """
        loss = self.mse_loss(predict, truth)
        return loss


class BCELoss(nn.Module):
    def __init__(self):
        super(BCELoss, self).__init__()
        self.bce_loss = nn.BCELoss()

    def forward(self, truth, predict):
        """
        Args:
            truth: tensor, (N)
            predict: tenor, (N)
        Returns:
            output: loss value
        """
        loss = self.bce_loss(predict, truth)
        return loss


def masked_mse_torch(preds, labels, null_val=np.nan):
    """
    Accuracy with masking.
    :param preds:
    :param labels:
    :param null_val:
    :return:
    """
    if np.isnan(null_val):
        # mask = ~tf.is_nan(labels)
        mask = ~torch.isnan(labels)
    else:
        # mask = tf.not_equal(labels, null_val)
        mask = torch.ne(labels, null_val)
    # mask = tf.cast(mask, tf.float32)
    mask = mask.to(torch.float32)
    # mask /= tf.reduce_mean(mask)
    mask /= torch.mean(mask)
    # mask = tf.where(tf.is_nan(mask), tf.zeros_like(mask), mask)
    mask = torch.where(torch.isnan(mask), torch.zeros_like(mask), mask)
    # loss = tf.square(tf.subtract(preds, labels))
    loss = torch.pow(preds - labels, 2)
    loss = loss * mask
    # loss = tf.where(tf.is_nan(loss), tf.zeros_like(loss), loss)
    loss = torch.where(torch.isnan(loss), torch.zeros_like(loss), loss)
    return torch.mean(loss)


def masked_mae_torch(preds, labels, null_val=np.nan):
    """
    Accuracy with masking.
    :param preds:
    :param labels:
    :param null_val:
    :return:
    """
    if np.isnan(null_val):
        mask = ~torch.isnan(labels)
    else:
        mask = torch.ne(labels, null_val)
    mask = mask.to(torch.float32)
    mask /= torch.mean(mask)
    mask = torch.where(torch.isnan(mask), torch.zeros_like(mask), mask)
    loss = torch.abs(preds - labels)
    loss = loss * mask
    loss = torch.where(torch.isnan(loss), torch.zeros_like(loss), loss)
    return torch.mean(loss)


def masked_rmse_torch(preds, labels, null_val=np.nan):
    """
    Accuracy with masking.
    :param preds:
    :param labels:
    :param null_val:
    :return:
    """
    return torch.sqrt(masked_mse_torch(preds=preds, labels=labels, null_val=null_val))


def create_loss(loss_type, **kwargs):
    if loss_type == 'mse_loss':
        return convert_to_gpu(MSELoss())
    elif loss_type == 'bce_loss':
        return convert_to_gpu(BCELoss())
    elif loss_type == 'masked_rmse_loss':
        return masked_rmse_loss(kwargs['scaler'], 0.0)
    elif loss_type == 'masked_mse_loss':
        return masked_mse_loss(kwargs['scaler'], 0.0)
    else:
        raise ValueError("Unknown loss function.")


# Builds loss function.
def masked_mse_loss(scaler, null_val):
    def loss(**kwargs):
        preds = kwargs['predict']
        labels = kwargs['truth']
        if scaler:
            preds = scaler.inverse_transform(preds)
            labels = scaler.inverse_transform(labels)
        return masked_mse_torch(preds=preds, labels=labels, null_val=null_val)

    return loss


def masked_rmse_loss(scaler, null_val):
    def loss(**kwargs):
        preds = kwargs['predict']
        labels = kwargs['truth']
        if scaler:
            preds = scaler.inverse_transform(preds)
            labels = scaler.inverse_transform(labels)
        return masked_rmse_torch(preds=preds, labels=labels, null_val=null_val)

    return loss


def masked_mae_loss(scaler, null_val):
    def loss(**kwargs):
        preds = kwargs['predict']
        labels = kwargs['truth']
        if scaler:
            preds = scaler.inverse_transform(preds)
            labels = scaler.inverse_transform(labels)
        mae = masked_mae_torch(preds=preds, labels=labels, null_val=null_val)
        return mae

    return loss
