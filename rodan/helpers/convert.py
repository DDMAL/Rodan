import os
from celery import task

import PIL.Image
import PIL.ImageFile


@task(name="rodan.helpers.convert.ensure_compatible", ignore_result=True)
def ensure_compatible(image_path):
    image = PIL.Image.open(image_path).convert('RGB')
    width, height = image.size

    # takes every image uploaded to Rodan and converts them to
    # lossless PNG, ensuring that they are always compatible for
    # future processing.

    ## do conversion

    return True
