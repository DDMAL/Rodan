#!/usr/bin/env python
# coding: utf-8

import numpy as np
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from skimage import io
from skimage.color import rgb2gray, rgba2rgb
from skimage.util import img_as_float32, img_as_ubyte
from skimage.filters import gaussian, threshold_otsu
from skimage.morphology import binary_opening, binary_closing
from skimage.transform import rescale, rotate
from skimage.segmentation import flood_fill
import matplotlib.pyplot as plt



def get_image(path):
    image = cv2.cvtColor(cv2.imread(path), cv2.COLOR_RGB2BGR)
    return image

def fill_corners(input_image, fill_value=0, thresh=1, tol=None, fill_below_thresh=True):

    s = input_image.shape

    if (input_image[0,0] < thresh) == fill_below_thresh:
        input_image = flood_fill(input_image, (0, 0), fill_value, tolerance=tol)
    if (input_image[-1, 0] < thresh) == fill_below_thresh:
        input_image = flood_fill(input_image, (s[0] - 1, 0), fill_value, tolerance=tol)
    if (input_image[0, -1] < thresh) == fill_below_thresh:
        input_image = flood_fill(input_image, (0, s[1] - 1), fill_value, tolerance=tol)

    # This statement would cause the job to hang, but a statement like this could be used for the bottom right corner.
    # if input_image[-1, -1] < thresh:
    #     input_image = flood_fill(input_image, (-1, -1), 1, tolerance=tol)

    return input_image

def find_rotation_angle(img, coarse_bound=4, fine_bound=0.25, rescale_amt=0.25):
    num_trials = int(coarse_bound / fine_bound)
    img_resized = rescale(img, rescale_amt, order=0)

    def project_angles(img_to_project, angles_to_try):
        best_angle = 0
        highest_variation = 0
        for a in angles_to_try:
            rot_img = rotate(img_to_project, a, mode='edge')
            proj = np.sum(rot_img, 1).astype('int64')
            variation = np.sum(np.diff(proj) ** 2)
            if variation > highest_variation:
                highest_variation = variation
                best_angle = a
        return best_angle
    
    angles_to_try = np.linspace(-coarse_bound, coarse_bound, num_trials)
    print("finding coarse angle")
    coarse_angle = project_angles(img_resized, angles_to_try)

    angles_to_try = np.linspace(-fine_bound + coarse_angle, fine_bound + coarse_angle, int(num_trials/2))
    print("finding fine angle")
    fine_angle = project_angles(img_resized, angles_to_try)

    return fine_angle

# def get_kernel_size(img):
#     pixels = img.shape[0] * img.shape[1]

#     # (x1,y1) and (x2,y2) are mapping from pixels from kernel size that were
#     # determined experimentally

#     x1 = 4872* 6496
#     y1 = 2
#     x2 = 9322*13438
#     y2 = 6

#     slope = (y2-y1)/(x2-x1)
#     intercept = y1 - slope * x1
#     size = slope * pixels + intercept
#     print(size)
#     return max(1, int(size))

def get_kernel_size(img):
    height = img.shape[0]

    # (x1,y1) and (x2,y2) (x3,xy) are mapping from pixels from kernel size that were
    # determined experimentally
    # ideal kernel size is linear in the number of pixels, or quadratic in side length
    # two options: map pixels to kernel size with a linear function
    # or map side length to kernel size with a quadratic function
    # the latter is preferable because for multi column folios, the width can be arbitrarily large
    # but the ideal kernel size will still be quadratic in the image height

    # solve for the interpolating quadratic function
    x1 = 6496
    y1 = 2
    x2 = 9854
    y2 = 4
    x3 = 13438
    y3 = 6

    matrix = np.array([[x1 **2, x1, 1],
                       [x2 **2, x2, 1],
                       [x3 **2, x3, 1]])
    vector = np.array([y1, y2, y3])
    inverse = np.linalg.inv(matrix)
    # a, b, c cofficients of y = ax^2 + bx + c
    # note that for positive x, this function will not fall below 1.1
    coefficients = np.matmul(inverse, vector)
    # the kernel size
    size = coefficients[0] * (height ** 2) + coefficients[1] * height + coefficients[2]
    return max(1, round(size))

def preprocess_image(input_image):

    # ensure that all points which are transparent have RGB values of 255 (will become white when
    # converted to non-transparent grayscale.)

    fill_holes = get_kernel_size(input_image)

    input_image = img_as_float32(input_image)
    if len(input_image.shape) == 3 and input_image.shape[2] == 4:
        input_image = rgba2rgb(input_image)
    gray_img = img_as_ubyte(rgb2gray(input_image))

    # get the otsu threshold after running a flood fill on the corners, so that those huge clumps of
    # dark pixels don't mess up the statistics too much (we only care about text!)
    thresh = threshold_otsu(fill_corners(gray_img, fill_value=255, thresh=5, tol=1, fill_below_thresh=True))

    # now, fill corners of binarized images with black (value 0)
    img_blur = img_as_ubyte(img_as_ubyte(gray_img) < thresh)

    # now, fill corners of binarized images with black (value 0)
    img_blur_bin = fill_corners(img_blur, fill_value=0, thresh=1, tol=1, fill_below_thresh=False)

    # run smoothing on the blurred-binarized image so we get blobs of text in neat lines
    kernel = np.ones((fill_holes, fill_holes), np.uint8)
    img_cleaned = binary_opening(binary_closing(img_blur_bin, kernel), kernel)

    # find rotation angle of cleaned, smoothed image. use that to correct the rotation of the unsmoothed image
    print("finding rotation angle")
    angle = find_rotation_angle(img_cleaned)
    print("angle: ", angle)
    img_cleaned_rot = rotate(img_cleaned, angle, order=0, mode='edge') > 0

    return img_cleaned_rot



def calculate_via_slices(img):
    distances = {}
    for col in img.T:
        start_indicies = (col[:-1]) != (col[1:])
        if start_indicies.sum() == 0:
            continue
        split_indicies = np.nonzero(start_indicies)[0] + 1
        splits = np.split(col, split_indicies)
        for split in splits:
            if split[0] == 0:
                distance = len(split)
                if distance in distances:
                    distances[distance] += 1
                else:
                    distances[distance] = 1
    # distances[1] = 0
    print(sorted(distances, key=distances.get, reverse=True)[:5])
    return max(distances, key=distances.get)


if __name__ == "__main__":
    img = get_image('Test_Data/5r.jpg')
    print("preprocessing image")
    processed = preprocess_image(img)
    # save binarized image
    plt.imsave('Test_Data/debug.jpg', np.array(processed), cmap='gray')
    print("calculating distance")
    distance = calculate_via_slices(processed)
    print("distance: ", distance)
