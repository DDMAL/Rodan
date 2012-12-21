import PIL.Image
import PIL.ImageFile
from django.conf import settings

import os


def create_thumbnail(image_path, thumb_path, thumbnail_size):
    image = PIL.Image.open(image_path).convert('RGB')
    width, height = image.size

    if thumbnail_size != settings.ORIGINAL_SIZE:
        dimensions = (thumbnail_size, int(width / float(thumbnail_size) * height))
        image.thumbnail(dimensions, PIL.Image.ANTIALIAS)

    if not os.path.exists(os.path.dirname(thumb_path)):
        os.makedirs(os.path.dirname(thumb_path))

    image.save(thumb_path)

    # Return the image dimensions so they can be used later
    return width, height


def create_thumbnails(page):
    for thumbnail_size in settings.THUMBNAIL_SIZES:
        thumb_path = page.thumb_path(size=thumbnail_size)
        create_thumbnail(page.image_path, thumb_path, thumbnail_size)


# def create_thumbnails(image_path, result):
#     page = result.page
#     job = result.job_item.job

#     for thumbnail_size in settings.THUMBNAIL_SIZES:
#         thumb_path = page.get_thumb_path(size=thumbnail_size, job=job)
#         width, height = create_thumbnail(image_path, thumb_path, thumbnail_size)

#     page.latest_width = width
#     page.latest_height = height
#     page.save()
