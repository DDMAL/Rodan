import os
import tempfile
import shutil
from celery import task
from django.core.files import File
from django.conf import settings
import PIL.Image
import PIL.ImageFile
from rodan.models import Resource, ResourceType

@task(name="rodan.jobs.helpers.ensure_compatible")
def ensure_compatible(resource_id, claimed_mimetype=None):
    resource_query = Resource.objects.filter(uuid=resource_id)
    resource_info = resource_query.values('resource_type__mimetype', 'resource_file')[0]

    if not claimed_mimetype:
        mimetype = resource_info['resource_type__mimetype']
    else:
        mimetype = claimed_mimetype

    infile_path = resource_info['resource_file']
    tmpdir = tempfile.mkdtemp()
    tmpfile = os.path.join(tmpdir, 'temp.png')


    if mimetype.startswith('image'):
        image = PIL.Image.open(infile_path).convert('RGB')
        image.save(tmpfile)
        resource_query.update(resource_type=ResourceType.cached("image/rgb+png").uuid)
    else:
        shutil.copy(infile_path, tmpfile)
        resource_query.update(resource_type=ResourceType.cached("application/octet-stream").uuid)

    with open(tmpfile, 'rb') as f:
        resource_object = resource_query[0]
        resource_object.compat_resource_file.save("", File(f), save=False)  # We give an arbitrary name as Django will automatically find the compat_path according to upload_to
    shutil.rmtree(tmpdir)
    compat_resource_file_path = resource_object.compat_resource_file.path
    resource_query.update(compat_resource_file=compat_resource_file_path)

    return True


@task(name="rodan.jobs.helpers.create_thumbnails")
def create_thumbnails(resource_id):
    resource_object = Resource.objects.filter(uuid=resource_id).select_related('resource_type')[0]
    mimetype = resource_object.resource_type.mimetype

    if mimetype.startswith('image'):
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
