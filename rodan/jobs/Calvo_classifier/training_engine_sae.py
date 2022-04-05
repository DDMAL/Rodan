from __future__ import division

import cv2
import numpy as np
import random as rd
import os
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dropout, UpSampling2D, Concatenate
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.backend import image_data_format
#import keras
import tensorflow as tf
import threading


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
    conv1 = Conv2D(
        ff, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(inputs)
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


@threadsafe_generator  # Credit: https://anandology.com/blog/using-iterators-and-generators/
def createGenerator(input_images, segmented_images, idx_label, patch_height, patch_width, batch_size):
    while True:

        selected_page_idx = np.random.randint(len(input_images))  # Changed len to grs from gr
        gr = input_images[selected_page_idx]
        label = str(idx_label)
        gt = segmented_images[selected_page_idx][label]

        potential_training_examples = np.where(gt[:-patch_height, :-patch_width] == 1)

        gr_chunks = []
        gt_chunks = []

        num_coords = len(potential_training_examples[0])

        index_coords_selected = [
            np.random.randint(0, num_coords) for _ in range(batch_size)
        ]
        x_coords = potential_training_examples[0][index_coords_selected]
        y_coords = potential_training_examples[1][index_coords_selected]

        for i in range(batch_size):
            row = x_coords[i]
            col = y_coords[i]
            gr_sample = gr[
                row : row + patch_height, col : col + patch_width
            ]  # Greyscale image
            gt_sample = gt[
                row : row + patch_height, col : col + patch_width
            ]  # Ground truth
            gr_chunks.append(gr_sample)
            gt_chunks.append(gt_sample)

        gr_chunks_arr = np.array(gr_chunks)
        gt_chunks_arr = np.array(gt_chunks)
        # convert gr_chunks and gt_chunks to the numpy arrays that are yield below

        yield gr_chunks_arr, gt_chunks_arr  # convert into npy before yielding


def getTrain(input_images, gts, num_labels, patch_height, patch_width, batch_size):
    generator_labels = []

    print("num_labels", num_labels)
    for idx_label in range(num_labels):
        print("idx_label", idx_label)
        generator_label = createGenerator(
            input_images, gts, idx_label, patch_height, patch_width, batch_size
        )
        generator_labels.append(generator_label)
        print(generator_labels)

    return generator_labels


def train_msae(
    input_images,
    gts,
    num_labels,
    height,
    width,
    output_path,
    epochs,
    max_samples_per_class,
    batch_size=16,
):

    # Create ground_truth
    print("Creating data generators...")
    generators = getTrain(input_images, gts, num_labels, height, width, batch_size)
    # Training loop
    for label in range(num_labels):
        print("Training a new model for label #{}".format(str(label)))
        model = get_sae(height=height, width=width)
        # model.summary()
        new_output_path = os.path.join(output_path[str(label)] + '.h5')
        callbacks_list = [
            ModelCheckpoint(
                new_output_path,
                save_best_only=True,
                monitor="val_accuracy",
                verbose=1,
                mode="max",
            ),
            EarlyStopping(monitor="val_accuracy", patience=3, verbose=0, mode="max"),
        ]

        # Training stage
        model.fit(
            generators[label],
            verbose=2,
            steps_per_epoch=max_samples_per_class // batch_size,
            validation_data=generators[label],
            validation_steps=100,
            callbacks=callbacks_list,
            epochs=epochs,
        )
        os.rename(new_output_path, output_path[str(label)])

    return 0


# Debugging code
if __name__ == "__main__":
    print("Must be run from Rodan")