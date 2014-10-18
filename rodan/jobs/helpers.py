import os
import tempfile
import shutil
from celery import task
from django.core.files import File
from django.conf import settings
import PIL.Image
import PIL.ImageFile
from rodan.models import Resource

@task(name="rodan.jobs.helpers.ensure_compatible")
def ensure_compatible(resource_id):
    resource_object = Resource.objects.prefetch_related('resource_types').get(uuid=resource_id)
    resource_types = resource_object.resource_types.all().values_list('name', flat=True)

    resource_file_path = resource_object.resource_file.path

    if 'image' in resource_types:
        filename = "compat_file.png"
        image = PIL.Image.open(resource_file_path).convert('RGB')
        tmpdir = tempfile.mkdtemp()
        image.save(os.path.join(tmpdir, filename))
        with open(os.path.join(tmpdir, filename), 'rb') as f:
            resource_object.compat_resource_file.save("", File(f), save=False)  # We give an arbitrary name as Django will automatically find the compat_path according to upload_to
            compat_resource_file_path = resource_object.compat_resource_file.path
        shutil.rmtree(tmpdir)
    else:
        with open(resource_file_path, 'rb') as f:
            resource_object.compat_resource_file.save("", File(f), save=False)  # We give an arbitrary name as Django will automatically find the compat_path according to upload_to
            compat_resource_file_path = resource_object.compat_resource_file.path

    Resource.objects.filter(uuid=resource_id).update(compat_resource_file=compat_resource_file_path)
    return True


@task(name="rodan.jobs.helpers.create_thumbnails")
def create_thumbnails(resource_id):
    resource_object = Resource.objects.prefetch_related('resource_types').get(uuid=resource_id)
    resource_types = resource_object.resource_types.all().values_list('name', flat=True)

    if 'image' in resource_types:
        image = PIL.Image.open(resource_object.compat_resource_file.path).convert('RGB')
        width = float(image.size[0])
        height = float(image.size[1])

        for thumbnail_size in settings.THUMBNAIL_SIZES:
            thumbnail_size = float(thumbnail_size)
            ratio = min((thumbnail_size / width), (thumbnail_size / height))
            dimensions = (int(width * ratio), int(height * ratio))

            thumbnail_size = str(int(thumbnail_size))
            thumb_copy = image.resize(dimensions, PIL.Image.ANTIALIAS)
            thumb_copy.save(os.path.join(resource_object.thumb_path,
                                         resource_object.thumb_filename(size=thumbnail_size)))

            del thumb_copy
        del image
        return True
    else:
        return False
