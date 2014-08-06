import os
import tempfile
import shutil
import warnings
from celery import task
from django.core.files import File
import PIL.Image
import PIL.ImageFile
from rodan.helpers.dbmanagement import exists_in_db, refetch_from_db


@task(name="rodan.helpers.convert.ensure_compatible", ignore_result=True)
def ensure_compatible(resource_object):
    resource_object = refetch_from_db(resource_object)

    filename = "compat_image.png"
    image = PIL.Image.open(resource_object.resource_file.path).convert('RGB')
    tmpdir = tempfile.mkdtemp()
    image.save(os.path.join(tmpdir, filename))

    compatible_resource_file_path = os.path.join(os.path.dirname(resource_object.resource_file.path), filename)
    f = open(os.path.join(tmpdir, filename), 'rb')

    if exists_in_db(resource_object):
        resource_object.compat_resource_file.save(compatible_resource_file_path, File(f))
    else:
        warnings.warn("The page was deleted from the database before it could be processed.")

    f.close()
    shutil.rmtree(tmpdir)

    return resource_object
