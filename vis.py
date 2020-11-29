import cv2
import numpy as np
import argparse
import os
import math
import json
import colorsys

def show_annots(idx, save=True):
    image_filename = "images/%05d.jpg"%idx
    img = cv2.imread(image_filename)
    pixels = np.load("annots/%05d.npy"%idx)
    vis = img.copy()
    print("Annotating %06d"%idx)
    for i, (u, v) in enumerate(pixels):
        (r, g, b) = colorsys.hsv_to_rgb(float(i)/len(pixels), 1.0, 1.0)
        R, G, B = int(255 * r), int(255 * g), int(255 * b)
        cv2.circle(vis,(int(u), int(v)), 1, (R, G, B), -1)
    if save:
    	annotated_filename = "%05d.jpg"%idx
    	cv2.imwrite('./vis/{}'.format(annotated_filename), vis)

if __name__ == '__main__':
    if os.path.exists("./vis"):
        os.system("rm -rf ./vis")
    os.makedirs("./vis")
    for i in range(len(os.listdir('images'))):
        show_annots(i)
