import os
from celery import task
from django.conf import settings
import PIL.Image
import PIL.ImageFile


@task(name="rodan.helpers.thumbnails.create_thumbnails")
def create_thumbnails(page_object):
    image = PIL.Image.open(page_object.page_image.path).convert('RGB')
    width = float(image.size[0])
    height = float(image.size[1])

    for thumbnail_size in settings.THUMBNAIL_SIZES:
        thumbnail_size = float(thumbnail_size)
        ratio = min((thumbnail_size / width), (thumbnail_size / height))
        dimensions = (int(width * ratio), int(height * ratio))

        thumbnail_size = str(int(thumbnail_size))
        thumb_copy = image.resize(dimensions, PIL.Image.ANTIALIAS)
        thumb_copy.save(os.path.join(page_object.thumb_path,
                                page_object.thumb_filename(size=thumbnail_size)))

        del thumb_copy
    del image

    return page_object
