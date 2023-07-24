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

def find_rotation_angle(img, coarse_bound=4, fine_bound=0.1, rescale_amt=0.25):
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

    angles_to_try = np.linspace(-fine_bound + coarse_angle, fine_bound + coarse_angle, num_trials)
    fine_angle = project_angles(img_resized, angles_to_try)

    return fine_angle

def preprocess_images(input_image, soften=5, fill_holes=5):
    # ensure that all points which are transparent have RGB values of 255 (will become white when
    # converted to non-transparent grayscale.)
    input_image = img_as_float32(input_image)
    if len(input_image.shape) == 3 and input_image.shape[2] == 4:
        input_image = rgba2rgb(input_image)
    gray_img = img_as_ubyte(rgb2gray(input_image))

    # get the otsu threshold after running a flood fill on the corners, so that those huge clumps of
    # dark pixels don't mess up the statistics too much (we only care about text!)
    thresh = threshold_otsu(fill_corners(gray_img, fill_value=255, thresh=5, tol=1, fill_below_thresh=True))

    # n.b. here we are setting black pixels from the original image to have a value of 1 (effectively inverting
    # what you would get from a normal binarization, because the math gets easier this way)
    img_bin = img_as_ubyte(gray_img < thresh)
    img_blur_bin = img_as_ubyte(img_as_ubyte(gaussian(gray_img, soften)) < thresh)

    # now, fill corners of binarized images with black (value 0)
    img_bin = fill_corners(img_bin, fill_value=0, thresh=1, tol=1, fill_below_thresh=False)
    img_blur_bin = fill_corners(img_blur_bin, fill_value=0, thresh=1, tol=1, fill_below_thresh=False)

    # run smoothing on the blurred-binarized image so we get blobs of text in neat lines
    kernel = np.ones((fill_holes, fill_holes), np.uint8)
    img_cleaned = binary_opening(binary_closing(img_blur_bin, kernel), kernel)

    # find rotation angle of cleaned, smoothed image. use that to correct the rotation of the unsmoothed image
    angle = find_rotation_angle(img_cleaned)
    img_cleaned_rot = rotate(img_cleaned, angle, order=0, mode='edge') > 0
    img_bin_rot = rotate(img_bin, angle, order=0, mode='edge') > 0

    return img_bin_rot, img_cleaned_rot, angle

def plot_image(image, title, cmap=None):
    plt.figure(figsize=(6, 6))  # You can adjust the size as needed
    plt.imshow(image, cmap=cmap)
    plt.title(title)  # Optional title
    plt.axis('off')  # To hide axis values
    plt.show()

def plot_histogram(histogram):
    plt.figure(figsize=(20, 10))
    plt.plot(range(len(histogram)), histogram)
    plt.xlabel('Row')
    plt.ylabel('Count of 1s')
    plt.title('Count of 1s in each row')
    plt.show()

def calculate_via_histogram(img):
    histogram = np.sum(img, axis=1)
    threshold = np.mean(histogram) + 2 * np.std(histogram)
    filtered = np.where(histogram < threshold, 0, threshold)
    peak_indices = np.where(filtered != 0)[0]
    distances = np.diff(peak_indices)
    return np.mean(distances)


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
    return max(distances, key=distances.get)


ein_img = get_image("Test_Data/Einsie.jpg")

# ein_bin_rot, ein_cleaned_rot, ein_angle = preprocess_images(ein_img)

# plt.imsave("Test_Data/ein_bin.png",ein_bin_rot,cmap='gray')
ein_bin_rot = io.imread("Test_Data/ein_bin.png", as_gray=True)

# hist_dist = calculate_via_histogram(ein_bin_rot)
slice_dist = calculate_via_slices(ein_bin_rot)

# print("Histogram distance: ", hist_dist)
print("Slice distance: ", slice_dist)