import os
import tempfile
import shutil
from celery import task
from django.core.files import File
from django.conf import settings
import PIL.Image
import PIL.ImageFile
from rodan.models import Resource, ResourceType
from rodan.models.resource import ResourceProcessingStatus
from celery import Task

class ensure_compatible(Task):
    name = "rodan.core.ensure_compatible"

    def run(self, resource_id, claimed_mimetype=None):
        resource_query = Resource.objects.filter(uuid=resource_id)
        resource_query.update(processing_status=ResourceProcessingStatus.RUNNING)
        resource_info = resource_query.values('resource_type__mimetype', 'resource_file')[0]

        if not claimed_mimetype:
            mimetype = resource_info['resource_type__mimetype']
        else:
            mimetype = claimed_mimetype

        infile_path = resource_info['resource_file']
        self._tmpdir = tempfile.mkdtemp()
        tmpfile = os.path.join(self._tmpdir, 'temp')

        inputs = {'in': [{
            'resource_path': infile_path,
            'resource_type': mimetype
        }]}
        outputs = {'out': [{
            'resource_path': tmpfile,
            'resource_type': ''
        }]}

        self._task_instance = None
        new_processing_status = ResourceProcessingStatus.HAS_FINISHED

        if mimetype.startswith('image'):
            from rodan.jobs.conversion.to_png import to_png
            self._task_instance = to_png()
            self._task_instance.run_my_task(inputs, [], outputs)
            resource_query.update(resource_type=ResourceType.cached("image/rgb+png").uuid)
        else:
            shutil.copy(infile_path, tmpfile)
            resource_query.update(resource_type=ResourceType.cached("application/octet-stream").uuid)
            new_processing_status = ResourceProcessingStatus.NOT_APPLICABLE

        with open(tmpfile, 'rb') as f:
            resource_object = resource_query[0]
            resource_object.compat_resource_file.save("", File(f), save=False)  # We give an arbitrary name as Django will automatically find the compat_path and extension according to upload_to and resource_type
        compat_resource_file_path = resource_object.compat_resource_file.path
        resource_query.update(compat_resource_file=compat_resource_file_path,
                              processing_status=new_processing_status)
        shutil.rmtree(self._tmpdir)
        del self._tmpdir
        del self._task_instance
        return True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        resource_id = args[0]
        update = self._task_instance._add_error_information_to_runjob(exc, einfo)
        update['processing_status'] = ResourceProcessingStatus.FAILED
        Resource.objects.filter(pk=resource_id).update(**update)
        shutil.rmtree(self._tmpdir)
        del self._tmpdir
        del self._task_instance


@task(name="rodan.core.create_thumbnails")
def create_thumbnails(resource_id):
    resource_query = Resource.objects.filter(uuid=resource_id).select_related('resource_type')
    resource_object = resource_query[0]
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
        resource_query.update(has_thumb=True)
        return True
    else:
        return False
