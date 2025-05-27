#!/usr/bin/env python
# coding: utf-8

import numpy as np
from skimage.color import rgb2gray, rgba2rgb
from skimage.util import img_as_float32, img_as_ubyte
from skimage.filters import threshold_yen
from skimage.morphology import binary_opening, binary_closing
from skimage.transform import rescale, rotate
from skimage.segmentation import flood_fill


def fill_corners(input_image, fill_value=0, thresh=1, tol=None, fill_below_thresh=True):
    # fills the corners of an image with a given value
    # taken from the text alignment job

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
    # finds the optimal rotation angle that maximizes the straightness of lines
    # taken from the text alginment job
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
    coarse_angle = project_angles(img_resized, angles_to_try)

    angles_to_try = np.linspace(-fine_bound + coarse_angle, fine_bound + coarse_angle, int(num_trials/2))
    fine_angle = project_angles(img_resized, angles_to_try)

    return fine_angle

# def get_kernel_size(img):
#     pixels = img.shape[0] * img.shape[1]

#     # (x1,y1) and (x2,y2) are mapping from pixels from kernel size that were
#     # determined experimentally

#     x1 = 4872* 6496
#     y1 = 4
#     x2 = 9322*13438
#     y2 = 7

#     slope = (y2-y1)/(x2-x1)
#     intercept = y1 - slope * x1
#     size = slope * pixels + intercept
#     return max(1, int(round(size)))

def get_kernel_size(img):
    height = img.shape[0]

    # (x1,y1) and (x2,y2) (x3,y3) are mappings from pixels from kernel size that were
    # determined experimentally
    # ideal kernel size is linear in the number of pixels, or quadratic in side length
    # two options: map pixels to kernel size with a linear function
    # or map side length to kernel size with a quadratic function
    # the latter is preferable because for multi column folios, the width can be arbitrarily large
    # but the ideal kernel size will still be quadratic in the image height

    # it's possible this is overkill and a linear function would be fine

    # solve for the interpolating quadratic function
    x1 = 6496
    y1 = 4
    x2 = 9854
    y2 = 5
    x3 = 13438
    y3 = 7

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
    return max(1, int(round(size)))

def preprocess_image(input_image):

    # converts 

    fill_holes = get_kernel_size(input_image)
    input_image = img_as_float32(input_image)
    if len(input_image.shape) == 3 and input_image.shape[2] == 4:
        input_image = rgba2rgb(input_image)
    gray_img = img_as_ubyte(rgb2gray(input_image))

    # get the yen threshold after running a flood fill on the corners, so that those huge clumps of
    # dark pixels don't mess up the statistics too much (we only care about text!)
    thresh = threshold_yen(fill_corners(gray_img, fill_value=255, thresh=5, tol=1, fill_below_thresh=True))
    # now, fill corners of binarized images with black (value 0)
    img_thresh = img_as_ubyte(img_as_ubyte(gray_img) < thresh)
    # now, fill corners of binarized images with black (value 0)
    img_blur_bin = fill_corners(img_thresh, fill_value=0, thresh=1, tol=1, fill_below_thresh=False)

    
    # find rotation angle of cleaned, smoothed image. use that to correct the rotation of the unsmoothed image
    angle = find_rotation_angle(img_blur_bin)
    img_rot = rotate(img_blur_bin, angle, order=0, mode='edge') > 0

    # despeckle the image then fill holes
    # use rectangular kernel for despeckle to punish non staff lines
    kernel1 = np.ones((fill_holes, fill_holes*4), np.uint8)
    kernel2 = np.ones((fill_holes, fill_holes), np.uint8)
    img_cleaned_rot = binary_opening(img_rot, kernel1)
    img_cleaned_rot = binary_closing(img_cleaned_rot, kernel2)

    return img_cleaned_rot != 0



def calculate_via_slices(img):
    # calculate the staff line distance by looking at the vertical slices of the image
    # counts the lengths of black pixels and returns the most common length
    distances = {}
    for col in img.T:
        # true at indices where the value changes
        start_indices = (col[:-1]) != (col[1:])
        if start_indices.sum() == 0:
            continue
        # get list of those indexes
        split_indices = np.nonzero(start_indices)[0] + 1
        # split the column at those indices
        splits = np.split(col, split_indices)
        for split in splits:
            # if a run of black, count the length
            if split[0] == 0:
                distance = len(split)
                if distance in distances:
                    distances[distance] += 1
                else:
                    distances[distance] = 1
    # return most common length
    return max(distances, key=distances.get)
