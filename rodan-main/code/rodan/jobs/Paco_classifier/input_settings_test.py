import cv2
import numpy as np
import logging

def pre_training_check(inputs, batch_size, patch_height, patch_width, number_samples_per_class):
    # Check if batch size is less than number of samples per class
    logging.info("Checking batch size")
    checkBatch(batch_size, number_samples_per_class)
    # Check if all images are larger than or equal to patch height and patch width
    num_pages_training = len(inputs["Image"])
    for layer in inputs:
        logging.info("Checking layer {}".format(layer))
        count = 0
        for img_path in inputs[layer]:
            # Import image with cv2
            img = open_image(img_path['resource_path'])
            # Check if image size is larger or equal to patch size
            check_size(img, patch_height, patch_width)
            # Check if image is non-empty if it isn't original image
            if layer != "Image":
                count += check_empty(img)
        # Check if an entire layer is does not only contain empty images
        if count >= num_pages_training:
            raise Exception('All images in layer {} are empty'.format(layer))
    
def check_size(img, patch_height, patch_width):
    if img.shape[0] < patch_height:
        raise ValueError('Patch height of {} is larger than image height of {}'.format(patch_height, img.shape[0]))
    if img.shape[1] < patch_width:
        raise ValueError('Patch height of {} is larger than image height of {}'.format(patch_width, img.shape[1]))

def check_empty(img):
    TRANSPARENCY = 3
    bg_mask = (img[:, :, TRANSPARENCY] == 255)
    
    return int(np.sum(bg_mask) == 0)

def checkBatch(batch_size, number_samples_per_class):
    if batch_size > number_samples_per_class:
        raise ValueError("Not enough samples for on batch, got batchsize: {} and number_samples_per_class: {}".format(batch_size, number_samples_per_class))

def open_image(image_path):
    file_obj = cv2.imread(image_path, cv2.IMREAD_UNCHANGED,)  # 4-channel
    if file_obj is None : 
        raise Exception(
            'It is not possible to load the image\n'
            "Path: " + str(image_path)
        )
    return file_obj
