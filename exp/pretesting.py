# -*- coding: utf-8 -*-
"""pretesting.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZEhjZH3oHRcRrAm_ng97LPzj36CArfrJ
"""

import numpy as np
import torch
import time
import logging
from sklearn.metrics import roc_auc_score

def pretest(testloader, autoencoder, device='cuda'):
        logger = logging.getLogger()

        # Set device for network
        autoencoder = autoencoder.to(device)

        # Testing
        logger.info('Testing autoencoder...')
        loss_epoch = 0.0
        n_batches = 0
        start_time = time.time()
        idx_label_score = []
        autoencoder.eval()
        with torch.no_grad():
            for data in testloader:
                inputs, labels, idx = data
                inputs = inputs.to(device)
                outputs = autoencoder(inputs)
                scores = torch.sum((outputs - inputs) ** 2, dim=tuple(range(1, outputs.dim())))
                loss = torch.mean(scores)

                # Save triple of (idx, label, score) in a list
                idx_label_score += list(zip(idx.cpu().data.numpy().tolist(),
                                            labels.cpu().data.numpy().tolist(),
                                            scores.cpu().data.numpy().tolist()))

                loss_epoch += loss.item()
                n_batches += 1

        logger.info('Test set Loss: {:.8f}'.format(loss_epoch / n_batches))

        _, labels, scores = zip(*idx_label_score)
        labels = np.array(labels)
        scores = np.array(scores)

        auc = roc_auc_score(labels, scores)
        logger.info('Test set AUC: {:.2f}%'.format(100. * auc))

        test_time = time.time() - start_time
        logger.info('Autoencoder testing time: %.3f' % test_time)
        logger.info('Finished testing autoencoder.')