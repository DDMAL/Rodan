import os
import math
from celery import task
from django.conf import settings
import PIL.Image
import PIL.ImageFile


@task(name="rodan.helpers.thumbnails.create_thumbnails", ignore_result=True)
def create_thumbnails(page_object):
    image = PIL.Image.open(page_object.page_image.path).convert('RGB')
    width, height = image.size

    for thumbnail_size in settings.THUMBNAIL_SIZES:
        dimensions = (thumbnail_size, int(math.ceil((thumbnail_size / float(height)) * width)))

        thumb_copy = image.resize(dimensions, PIL.Image.ANTIALIAS)
        thumb_copy.save(os.path.join(page_object.thumb_path,
                                page_object.thumb_filename(size=thumbnail_size)))

        del thumb_copy
    del image

    return page_object
