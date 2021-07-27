# Calvo-classifier

Repository of the Rodan wrapper for Calvo classifier

# Rodan Jobs definition
This repository includes the following Rodan Jobs:
- `Pixelwise Analysis of Music Document` in **calvo_classifier.py**
- `Training model for Pixelwise Analysis of Music Document` in **calvo_trainer.py**
- `Fast Pixelwise Analysis of Music Document` in **fast_calvo_classifier.py**
  - Available in the **python3** Rodan queue.
- `Training model for Patchwise Analysis of Music Document` in **fast_calvo_trainer.py**
  - Available in the **python3** Rodan queue.

# Installation Dependencies

## Python dependencies:

  * h5py (2.7.0)
  * html5lib (0.9999999)
  * Keras (2.0.5)
  * numpy (1.15.1)
  * scipy (0.19.1)
  * setuptools (36.0.1)
  * six (1.10.0)
  * Tensorflow (1.5)
  * opencv-python (3.2.0.7)

## Keras configuration

Calvo's classifier needs *Keras* and *TensorFlow* to be installed. It can be easily done through **pip**. 

*Keras* works over both Theano and Tensorflow, so after the installation check **~/.keras/keras.json** so that it looks like:

~~~
{
    "image_dim_ordering": "tf",
    "epsilon": 1e-07,
    "floatx": "float32",
    "backend": "tensorflow"
}
~~~

