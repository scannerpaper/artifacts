import random
import cv2
import numpy as np
from mmdet.datasets import PIPELINES


@PIPELINES.register_module()
class RandomFlipColor:
    def __init__(self, p=0.5):
        self.p = p
    
    def __call__(self, results):
        if random.random() > self.p:
            return results

        img = results['img']
        img = 255 - img
        results['img'] = img
        return results


@PIPELINES.register_module()
class RandomGrayscale:
    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, results):
        if random.random() > self.p:
            return results

        img = results['img']
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = np.expand_dims(img, -1)
        img = np.tile(img, (1, 1, 3))
        results['img'] = img
        return results


@PIPELINES.register_module()
class RandomBlur:
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, results):
        ksizes = np.arange(1, self.max_size, 2)
        ksize = np.random.choice(ksizes)
        if ksize == 1:
            return results
        
        img = results['img']
        img = cv2.blur(img, (ksize, ksize))
        results['img'] = img
        return results