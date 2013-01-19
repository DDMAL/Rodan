import os
from celery import task

import PIL.Image
import PIL.ImageFile


@task(name="rodan.helpers.thumbnails.create_thumbnail", ignore_result=True)
def create_thumbnail(image_path, thumb_path, thumbnail_size):
    image = PIL.Image.open(image_path).convert('RGB')
    width, height = image.size

    dimensions = (thumbnail_size, int(width / float(thumbnail_size) * height))
    image.thumbnail(dimensions, PIL.Image.ANTIALIAS)

    if not os.path.exists(os.path.dirname(thumb_path)):
        os.makedirs(os.path.dirname(thumb_path))
    image.save(thumb_path)
    return True
