from __future__ import division

import cv2
import numpy as np
import random as rd
import os
import copy
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dropout, UpSampling2D, Concatenate
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Input, Masking
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.backend import image_data_format
#import keras
import tensorflow as tf
import threading
from enum import Enum

import logging

kPIXEL_VALUE_FOR_MASKING = -1

class FileSelectionMode(Enum):
    RANDOM,     \
    SHUFFLE,    \
    DEFAULT     \
    = range(3)

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return FileSelectionMode[s]
        except KeyError:
            raise ValueError()

class SampleExtractionMode(Enum):
    RANDOM,     \
    SEQUENTIAL  \
    = range(2)

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return SampleExtractionMode[s]
        except KeyError:
            raise ValueError()

# ===========================
#       SETTINGS
# ===========================

# gpu_options = tf.GPUOptions(
#     allow_growth=True,
#     per_process_gpu_memory_fraction=0.40
# )
# sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
# keras.backend.tensorflow_backend.set_session(sess)
VALIDATION_SPLIT = 0.2
# BATCH_SIZE = 16
# ===========================


# ===========================
#       CONSTANTS
# ===========================
KEY_BACKGROUND_LAYER = "rgba PNG - Layer 0 (Background)"
KEY_SELECTED_REGIONS = "rgba PNG - Selected regions"
KEY_RESOURCE_PATH = "resource_path"
# ===========================

class threadsafe_iter:
    """Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    """

    def __init__(self, it):
        self.it = it
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.it)


def get_input_shape(height, width, channels=3):
    if image_data_format() == "channels_first":
        return (channels, height, width)
    else:
        return (height, width, channels)


def get_sae(height, width, pretrained_weights=None):
    ff = 32

    inputs = Input(shape=get_input_shape(height, width))
    mask = Masking(mask_value=kPIXEL_VALUE_FOR_MASKING)(inputs)

    conv1 = Conv2D(
        ff, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(mask)
    conv1 = Conv2D(
        ff, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
    conv2 = Conv2D(
        ff * 2, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(pool1)
    conv2 = Conv2D(
        ff * 2, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(
        ff * 8, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(pool2)
    conv7 = Conv2D(
        ff * 8, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv3)
    up8 = UpSampling2D(size=(2, 2))(conv7)
    up8 = Conv2D(
        ff * 4, 2, activation="relu", padding="same", kernel_initializer="he_normal"
    )(up8)
    merge8 = Concatenate(axis=3)([conv2, up8])

    conv8 = Conv2D(
        ff * 4, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(merge8)
    conv8 = Conv2D(
        ff * 4, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv8)
    up9 = UpSampling2D(size=(2, 2))(conv8)
    up9 = Conv2D(
        ff * 2, 2, activation="relu", padding="same", kernel_initializer="he_normal"
    )(up9)
    merge9 = Concatenate(axis=3)([conv1, up9])

    conv9 = Conv2D(
        ff * 2, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(merge9)
    conv9 = Conv2D(
        ff * 2, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv9)
    conv9 = Conv2D(
        2, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv9)
    conv10 = Conv2D(1, 1, activation="sigmoid")(conv9)

    model = Model(inputs=inputs, outputs=conv10)

    model.compile(
        optimizer=Adam(lr=1e-4), loss="binary_crossentropy", metrics=["accuracy"]
    )

    if pretrained_weights is not None:
        model.load_weights(pretrained_weights)

    return model


def threadsafe_generator(f):
    """A decorator that takes a generator function and makes it thread-safe."""

    def g(*a, **kw):
        return threadsafe_iter(f(*a, **kw))

    return g

#Load a Ground-truth image and apply the region mask if it is given
def load_gt_image(path_file, regions_mask=None):
    file_obj = cv2.imread(path_file, cv2.IMREAD_UNCHANGED,)  # 4-channel
    if file_obj is None : 
        raise Exception(
            'It is not possible to load the image\n'
            "Path: " + str(path_file)
        )

    TRANSPARENCY = 3
    bg_mask = (file_obj[:, :, TRANSPARENCY] == 255)
    
    if regions_mask is not None:
        masked = np.logical_and(bg_mask, regions_mask)
        return masked
    else:
        return bg_mask

def get_gt_image_and_regions(inputs, idx_label, idx_file):
    regions_mask = load_gt_image(inputs[KEY_SELECTED_REGIONS][idx_file][KEY_RESOURCE_PATH])

    if idx_label == 0:
        gt_path_file = inputs[KEY_BACKGROUND_LAYER][idx_file][KEY_RESOURCE_PATH]
    else:
        input_ports = len([x for x in inputs if "Layer" in x])
        if idx_label >= input_ports : # If we try to access to an non-existing layer 
            raise Exception(
                'The index of the layer does not exist\n'
                "input_ports: " + str(input_ports) + " index acceded: " + str(idx_label)
            )

        gt_path_file = inputs["rgba PNG - Layer {layer_num}".format(layer_num=idx_label)][idx_file][KEY_RESOURCE_PATH]
        
    gt = load_gt_image(gt_path_file, regions_mask)
    return gt, regions_mask

def get_image_with_gt(inputs, idx_file, idx_label):

    # Required input ports
    # TODO assert that all layers have the same number of inputs (otherwise it will crack afterwards)
    number_of_training_pages = len(inputs["Image"])
    if idx_file >= number_of_training_pages : # If we try to access to an non-existing layer 
        raise Exception(
            'The index of the file does not exist\n'
            "input images: " + str(number_of_training_pages) + " index acceded: " + str(idx_file)
        )

    gt, regions_mask = get_gt_image_and_regions(inputs, idx_label, idx_file)
    gr = cv2.imread(inputs["Image"][idx_file][KEY_RESOURCE_PATH], cv2.IMREAD_COLOR)  # 3-channel
    gr = (255.-gr) / 255.

    #Deactivate the training process for pixels outside the region mask
    l = np.where((regions_mask == 0))
    gr[l] = kPIXEL_VALUE_FOR_MASKING

    return gr, gt

def appendNewSample(gr, gt, row, col, patch_height, patch_width, gr_chunks, gt_chunks):
    gr_sample = gr[
            row : row + patch_height, col : col + patch_width
        ]  # Greyscale image
    gt_sample = gt[
        row : row + patch_height, col : col + patch_width
    ]  # Ground truth
    gr_chunks.append(gr_sample)
    gt_chunks.append(gt_sample)



def createGeneratorSingleFileSequentialExtraction(inputs, idx_file, idx_label, row, col, patch_height, patch_width, batch_size):
    gr, gt = get_image_with_gt(inputs, idx_file, idx_label)

    gr_chunks = []
    gt_chunks = []

    hstride = patch_height // 2
    wstride = patch_width // 2
    
    count = 0
    for r in range(row, gr.shape[0] - patch_height, hstride):
        for c in range(col, gr.shape[1] - patch_width, wstride):
            appendNewSample(gr, gt, row, col, patch_height, patch_width, gr_chunks, gt_chunks)
            count +=1
            if count % batch_size == 0:
                gr_chunks_arr = np.array(gr_chunks)
                gt_chunks_arr = np.array(gt_chunks)
                # convert gr_chunks and gt_chunks to the numpy arrays that are yield below

                return gr_chunks_arr, gt_chunks_arr, r, c  # convert into npy before yielding



def extractRandomSamplesClass(gr, gt, idx_class, patch_height, patch_width, batch_size, gr_chunks, gt_chunks):
    potential_training_examples = np.where(gt[:-patch_height, :-patch_width] == 1)

    num_coords = len(potential_training_examples[0])

    if num_coords >= batch_size:

        index_coords_selected = [
            np.random.randint(0, num_coords) for _ in range(batch_size)
        ]
        x_coords = potential_training_examples[0][index_coords_selected]
        y_coords = potential_training_examples[1][index_coords_selected]
    else:
        x_coords = [
            np.random.randint(0, gr.shape[0]) for _ in range(batch_size)
        ]

        y_coords = [
            np.random.randint(0, gr.shape[1]) for _ in range(batch_size)
        ]

    for i in range(batch_size):
        row = x_coords[i]
        col = y_coords[i]
        appendNewSample(gr, gt, row, col, patch_height, patch_width, gr_chunks, gt_chunks)


def extractRandomSamples(inputs, idx_file, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode):
    gr, gt = get_image_with_gt(inputs, idx_file, idx_label)

    
    gr_chunks = []
    gt_chunks = []

    num_samples_with_layer = batch_size // 2

    extractRandomSamplesClass(gr, gt, 1, patch_height, patch_width, num_samples_with_layer, gr_chunks, gt_chunks)
    extractRandomSamplesClass(gr, gt, 0, patch_height, patch_width, batch_size-num_samples_with_layer, gr_chunks, gt_chunks)

    gr_chunks_arr = np.array(gr_chunks)
    gt_chunks_arr = np.array(gt_chunks)
    # convert gr_chunks and gt_chunks to the numpy arrays that are yield below

    return gr_chunks_arr, gt_chunks_arr  # convert into npy before yielding


def get_stride(patch_height, patch_width):
    return patch_height // 2, patch_width // 2

@threadsafe_generator  # Credit: https://anandology.com/blog/using-iterators-and-generators/
def createGeneratorSequentialExtraction(inputs, idx_file, idx_label, patch_height, patch_width, batch_size):
    
    hstride, wstride = get_stride(patch_height, patch_width)
    
    gr_chunks = []
    gt_chunks = []

    gr, gt = get_image_with_gt(inputs, idx_file, idx_label)
    count = 0
    for row in range(0, gr.shape[0] - patch_height, hstride):
        for col in range(0, gr.shape[1] - patch_width, wstride):

            appendNewSample(gr, gt, row, col, patch_height, patch_width, gr_chunks, gt_chunks)
            count +=1
            if count % batch_size == 0:
                gr_chunks_arr = np.array(gr_chunks)
                gt_chunks_arr = np.array(gt_chunks)
                # convert gr_chunks and gt_chunks to the numpy arrays that are yield below

                yield gr_chunks_arr, gt_chunks_arr  # convert into npy before yielding
                gr_chunks = []
                gt_chunks = []
                count = 0


@threadsafe_generator  # Credit: https://anandology.com/blog/using-iterators-and-generators/
def createGeneratorDefault(inputs, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode):
    print("Creating default generator...")
    
    number_of_training_pages = len(inputs["Image"])

    while True:
        for idx_file in range(number_of_training_pages):
            if sample_extraction_mode == SampleExtractionMode.RANDOM:
                yield extractRandomSamples(inputs, idx_file, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode)
            elif sample_extraction_mode == SampleExtractionMode.SEQUENTIAL:
                for i in createGeneratorSequentialExtraction(inputs, idx_file, idx_label, patch_height, patch_width, batch_size):
                    yield i
            else:
                raise Exception(
                    'The sample extraction mode does not exist.\n'
                )


@threadsafe_generator  # Credit: https://anandology.com/blog/using-iterators-and-generators/
def createGeneratorShuffle(inputs, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode):
    print("Creating shuffle generator...")
    
    list_shuffle_idx_files = list(range(len(inputs["Image"])))
        
    while True:
        rd.shuffle(list_shuffle_idx_files)
        
        for idx_file in list_shuffle_idx_files:
            if sample_extraction_mode == SampleExtractionMode.RANDOM:
                yield extractRandomSamples(inputs, idx_file, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode)
            elif sample_extraction_mode == SampleExtractionMode.SEQUENTIAL:
                for i in createGeneratorSequentialExtraction(inputs, idx_file, idx_label, patch_height, patch_width, batch_size):
                    yield i
            else:
                raise Exception(
                    'The sample extraction mode does not exist.\n'
                )

@threadsafe_generator  # Credit: https://anandology.com/blog/using-iterators-and-generators/
def createGeneratorRandom(inputs, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode):
    print("Creating random generator...")

    number_of_training_pages = len(inputs["Image"])

    while True:
        idx_file = np.random.randint(number_of_training_pages)  # Changed len to grs from gr
        if sample_extraction_mode == SampleExtractionMode.RANDOM:
            yield extractRandomSamples(inputs, idx_file, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode)
        elif sample_extraction_mode == SampleExtractionMode.SEQUENTIAL:
            for i in createGeneratorSequentialExtraction(inputs, idx_file, idx_label, patch_height, patch_width, batch_size):
                yield i
        else:
            raise Exception(
                'The sample extraction mode does not exist.\n'
            )


def deleteImagesWith(inputs, idx_label):
    for idx_file in range(len(inputs["Image"])-1, -1, -1):
        
        gt, _ = get_gt_image_and_regions(inputs, idx_label, idx_file)

        if (np.sum(gt) == 0):
            inputs["Image"].pop(idx_file)
            inputs[KEY_SELECTED_REGIONS].pop(idx_file)
            inputs[KEY_BACKGROUND_LAYER].pop(idx_file)
    return inputs

@threadsafe_generator  # Credit: https://anandology.com/blog/using-iterators-and-generators/
def createGenerator(inputs, idx_label, patch_height, patch_width, batch_size, file_selection_mode, sample_extraction_mode):
    inputs_copy = copy.deepcopy(inputs)
    inputs_copy = deleteImagesWith(inputs_copy, idx_label)

    if file_selection_mode == FileSelectionMode.DEFAULT:
        return createGeneratorDefault(inputs_copy, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode)
    elif file_selection_mode == FileSelectionMode.SHUFFLE:
        return createGeneratorShuffle(inputs_copy, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode)
    elif file_selection_mode == FileSelectionMode.RANDOM:
        return createGeneratorRandom(inputs_copy, idx_label, patch_height, patch_width, batch_size, sample_extraction_mode)
    else:
        raise Exception(
            'The file extraction mode does not exist.\n'
        ) 



def getTrain(inputs, num_labels, patch_height, patch_width, batch_size, file_selection_mode, sample_extraction_mode):
    generator_labels = []

    print("num_labels", num_labels)
    for idx_label in range(num_labels):
        print("idx_label", idx_label)
        generator_label = createGenerator(
            inputs, idx_label, patch_height, patch_width, batch_size, file_selection_mode, sample_extraction_mode
        )
        generator_labels.append(generator_label)
        print(generator_labels)

    return generator_labels



def get_number_samples_sequential(inputs, patch_height, patch_width):
    hstride, wstride = get_stride(patch_height, patch_width)
    number_samples = 0

    for idx_file in range(len(inputs["Image"])):
        gr = cv2.imread(inputs["Image"][idx_file][KEY_RESOURCE_PATH], cv2.IMREAD_COLOR)  # 3-channel
        number_samples += ((gr.shape[0] - patch_height) // hstride) * ((gr.shape[1] - patch_width) // wstride)

    return number_samples

def get_steps_per_epoch(inputs, number_samples_per_class, patch_height, patch_width, batch_size, sample_extraction_mode):

    if sample_extraction_mode == SampleExtractionMode.RANDOM:
        return number_samples_per_class // batch_size
    elif sample_extraction_mode == SampleExtractionMode.SEQUENTIAL:
        return get_number_samples_sequential(inputs, patch_height, patch_width) // batch_size
    else:
        raise Exception(
            'The sample extraction mode does not exist.\n'
        )
        
    

def train_msae(
    inputs,
    num_labels,
    height,
    width,
    output_path,
    file_selection_mode,
    sample_extraction_mode,
    epochs,
    number_samples_per_class,
    batch_size=16,
    patience=15
):

    # Create ground_truth
    print("Creating data generators...")
    generators = getTrain(inputs, num_labels, height, width, batch_size, file_selection_mode, sample_extraction_mode)
    generators_validation = getTrain(inputs, num_labels, height, width, batch_size, FileSelectionMode.DEFAULT, SampleExtractionMode.RANDOM)

    # Training loop
    for label in range(num_labels):
        print("Training a new model for label #{}".format(str(label)))
        model = get_sae(height=height, width=width)
        # model.summary()
        new_output_path = os.path.join(output_path[str(label)])
        callbacks_list = [
            ModelCheckpoint(
                new_output_path,
                save_best_only=True,
                monitor="val_accuracy",
                verbose=1,
                mode="max",
            ),
            EarlyStopping(monitor="val_accuracy", patience=patience, verbose=0, mode="max"),
        ]

        steps_per_epoch = get_steps_per_epoch(inputs, number_samples_per_class, height, width, batch_size, sample_extraction_mode)

        # Training stage
        model.fit(
            generators[label],
            verbose=2,
            steps_per_epoch=steps_per_epoch,
            validation_data=generators_validation[label],
            validation_steps=100,
            callbacks=callbacks_list,
            epochs=epochs
        )
        
        os.rename(new_output_path, output_path[str(label)])

    return 0


# Debugging code
if __name__ == "__main__":
    print("Must be run from Rodan")
