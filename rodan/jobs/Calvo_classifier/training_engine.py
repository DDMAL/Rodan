import cv2
import numpy as np
import random as rd
import os
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Input
from tensorflow.keras.optimizers import Adadelta
from tensorflow.keras.callbacks import EarlyStopping,ModelCheckpoint
from tensorflow.keras.backend import image_data_format
from tensorflow.keras.layers import BatchNormalization

# ===========================
#       SETTINGS
# ===========================

VALIDATION_SPLIT=0.2
BATCH_SIZE = 16

# ===========================

def get_input_shape(height, width, channels = 3):
    if image_data_format() == 'channels_first':
        return (channels, height, width)
    else:
        return (height, width, channels)


def get_convnet(height, width, labels):
    img_input = Input(shape=get_input_shape(height,width))
    x = img_input

    for layer in range(1,5):
        x = Conv2D(filters=32*layer, kernel_size=(3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Flatten()(x)
    x = Dense(labels,activation='softmax')(x)
    return Model(img_input, x, name='calvonet')


def getTrain(input_image, gt, hspan, vspan, num_labels, max_samples_per_class):

    X_train = []
    Y_train = []

    # Speed-up factor
    factor = 10.

    # Calculate the ratio per label
    count = [0] * num_labels

    for page in range(len(input_image)):
        for i in range(num_labels):
            count[i] += (gt[page] == i).sum()

    samples_per_class = min(np.min(count), max_samples_per_class)

    ratio = [0] * num_labels
    for i in range(num_labels):
        ratio[i] = factor * (samples_per_class/float(count[i]))


    # Just for checking !
    count_per_class = [0] * num_labels

    # Get samples according to the ratio per label
    for page in range(len(input_image)):

        page_x = input_image[page]
        page_y = gt[page]

        [height, width] = page_y.shape

        for row in range(vspan,height-vspan-1):
            for col in range(hspan,width-hspan-1):

                if rd.random() < 1./factor:

                    label = page_y[row][col]

                    if 0 <= label < num_labels: # Avoid possible noise in the GT or -1 (unknown pixel)

                        if rd.random() < ratio[label]: # Take samples according to its

                            sample = page_x[row-vspan:row+vspan+1,col-hspan:col+hspan+1]

                            # Categorical vector
                            y_label = [0]*num_labels
                            y_label[label] = 1

                            X_train.append(sample)
                            Y_train.append(y_label)

                            count_per_class[label] += 1

    # Manage different ordering
    if image_data_format() == 'channels_first':
        X_train = np.asarray(X_train).reshape(len(X_train), 3, vspan*2 + 1, hspan*2 + 1)
    else:
        X_train = np.asarray(X_train).reshape(len(X_train), vspan*2 + 1, hspan*2 + 1, 3)

    Y_train = np.asarray(Y_train).reshape(len(Y_train), num_labels)

    print('Distribution of data per class: ' + str(count_per_class))

    return [X_train, Y_train]


def train_model(input_image, gt, hspan, vspan, output_model_path, max_samples_per_class, epochs, num_labels = 4):
    # -------------------------------------------------------------------------------------------------------------------

    # Create training set
    [X_train, Y_train] = getTrain([input_image], [gt],
                                  hspan, vspan,
                                  num_labels,
                                  max_samples_per_class=max_samples_per_class)

    print('Training created with ' + str(len(X_train)) + ' samples.')

    # Training configuration
    print('Training a new model')
    model = get_convnet(
        height=hspan * 2 + 1,
        width=vspan * 2 + 1,
        labels=num_labels
    )

    #model.summary()

    # In Tensorflow 2, it is necessary to add '.h5' to the end of the filename to force saving
    # in hdf5 format with a ModelCheckpoint. Rodan will not accept anything but the file's
    # original filename, however, so we must rename it back after training.
    new_output_path = os.path.join(output_model_path + '.h5')

    callbacks_list = [
            ModelCheckpoint(new_output_path, save_best_only=True, monitor='val_acc', verbose=1, mode='max'),
            EarlyStopping(monitor='val_acc', patience=3, verbose=0, mode='max')
            ]

    model.compile(loss='categorical_crossentropy',
                  optimizer=Adadelta(lr=1.0, rho=0.95, epsilon=1e-08, decay=0.0),
                  metrics=["accuracy"])

    # Training stage
    model.fit(X_train, Y_train,
              verbose=2,
              batch_size=BATCH_SIZE,
              validation_split=VALIDATION_SPLIT,
              callbacks=callbacks_list,
              epochs=epochs
              )

    # Rename the file back to what Rodan expects.
    os.rename(new_output_path, output_model_path)

    return 0
