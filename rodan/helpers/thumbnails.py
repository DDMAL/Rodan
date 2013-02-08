import os
import math
from celery import task
from django.conf import settings
import PIL.Image
import PIL.ImageFile


@task(name="rodan.helpers.thumbnails.create_thumbnails")
def create_thumbnails(page_object):
    image = PIL.Image.open(page_object.page_image.path).convert('RGB')
    width, height = image.size

    for thumbnail_size in settings.THUMBNAIL_SIZES:
        if width > height:
            dimensions = (thumbnail_size, int(math.ceil((height / (width / float(thumbnail_size))))))
        else:
            dimensions = (int(math.ceil((width / (height / float(thumbnail_size))))), thumbnail_size)

        thumb_copy = image.resize(dimensions, PIL.Image.ANTIALIAS)
        thumb_copy.save(os.path.join(page_object.thumb_path,
                                page_object.thumb_filename(size=thumbnail_size)))

        del thumb_copy
    del image

    return page_object
