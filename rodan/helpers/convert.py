import os
import tempfile
import shutil
from celery import task
from django.core.files import File
import PIL.Image
import PIL.ImageFile


@task(name="rodan.helpers.convert.ensure_compatible", ignore_result=True)
def ensure_compatible(page_object):
    filename = "compat_image.png"

    image = PIL.Image.open(page_object.page_image.path).convert('RGB')
    tmpdir = tempfile.mkdtemp()
    image.save(os.path.join(tmpdir, filename))

    compatible_image_path = os.path.join(page_object.image_path, filename)
    f = open(os.path.join(tmpdir, filename), 'rb')
    page_object.compat_page_image.save(compatible_image_path, File(f))
    f.close()
    shutil.rmtree(tmpdir)

    return page_object
