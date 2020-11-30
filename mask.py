import cv2
import numpy as np
import os

def mask_binary(idx, save=True):
    mask_filename = "masks/%05d.jpg"%idx
    mask = cv2.imread(mask_filename, 0)
    _, mask = cv2.threshold(mask,127,255,cv2.THRESH_BINARY)
    cv2.imwrite(mask_filename, mask)

if __name__ == '__main__':
    for i in range(len(os.listdir('masks'))):
        mask_binary(i)
