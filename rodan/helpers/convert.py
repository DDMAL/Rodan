import os
from celery import task
import PIL.Image
import PIL.ImageFile


@task(name="rodan.helpers.convert.ensure_compatible", ignore_result=True)
def ensure_compatible(page_object):
    image = PIL.Image.open(page_object.page_image.path).convert('RGB')
    compatible_image_path = os.path.join(page_object.image_path, "compat_image.png")
    image.save(compatible_image_path)
    return page_object
