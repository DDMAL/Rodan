import os
import tempfile
import shutil
import traceback
from pybagit.bagit import BagIt
from celery import task, registry
from django.core.files import File
from django.conf import settings
from django.db.models import Q
import PIL.Image
import PIL.ImageFile
from rodan.models import Resource, ResourceType, ResultsPackage, Output
from rodan.models.resultspackage import get_package_path
from rodan.constants import task_status
from celery import Task
from rodan.jobs.base import RodanAutomaticTask, TemporaryDirectory

class ensure_compatible(Task):
    name = "rodan.core.ensure_compatible"

    def run(self, resource_id, claimed_mimetype=None):
        resource_query = Resource.objects.filter(uuid=resource_id)
        resource_query.update(processing_status=task_status.PROCESSING)
        resource_info = resource_query.values('resource_type__mimetype', 'resource_file')[0]

        if not claimed_mimetype:
            mimetype = resource_info['resource_type__mimetype']
        else:
            mimetype = claimed_mimetype

        with TemporaryDirectory() as tmpdir:
            infile_path = resource_info['resource_file']
            tmpfile = os.path.join(tmpdir, 'temp')

            inputs = {'in': [{
                'resource_path': infile_path,
                'resource_type': mimetype
            }]}
            outputs = {'out': [{
                'resource_path': tmpfile,
                'resource_type': ''
            }]}

            new_processing_status = task_status.FINISHED

            if mimetype.startswith('image'):
                self._task = registry.tasks['rodan.jobs.conversion.to_png']
                self._task.run_my_task(inputs, [], outputs)
                resource_query.update(resource_type=ResourceType.cached("image/rgb+png").uuid)
            else:
                shutil.copy(infile_path, tmpfile)
                resource_query.update(resource_type=ResourceType.cached("application/octet-stream").uuid)
                new_processing_status = task_status.NOT_APPLICABLE

            with open(tmpfile, 'rb') as f:
                resource_object = resource_query[0]
                resource_object.compat_resource_file.save("", File(f), save=False)  # We give an arbitrary name as Django will automatically find the compat_path and extension according to upload_to and resource_type
                compat_resource_file_path = resource_object.compat_resource_file.path
                resource_query.update(compat_resource_file=compat_resource_file_path,
                                      processing_status=new_processing_status)
        return True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        resource_id = args[0]
        resource_query = Resource.objects.filter(uuid=resource_id)

        if hasattr(self, '_task'):
            update = self._task._add_error_information_to_runjob(exc, einfo)
            update['processing_status'] = task_status.FAILED
            resource_query.update(**update)
            del self._task
        else:
            resource_query.update(processing_status=task_status.FAILED,
                                  error_summary="{0}: {1}".format(type(exc).__name__, str(exc)),
                                  error_details=einfo.traceback)



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


class package_results(Task):
    name = "rodan.core.package_results"

    def run(self, rp_id, include_failed_runjobs=False):
        rp_query = ResultsPackage.objects.filter(uuid=rp_id)
        rp_query.update(status=task_status.PROCESSING, celery_task_id=self.request.id)
        rp = rp_query.first()
        package_path = get_package_path(rp_id)

        # Get endpoint outputs
        output_query = Output.objects.filter(Q(run_job__workflow_run=rp.workflow_run) &
                                             (Q(resource__inputs__isnull=True) | ~Q(resource__inputs__run_job__workflow_run=rp.workflow_run)))
        outputs = output_query.values('output_port_type_name',
                                      'run_job__uuid',
                                      'run_job__job_name',
                                      'resource__uuid',
                                      'resource__name',
                                      'resource__compat_resource_file',
                                      'run_job__status',
                                      'run_job__error_summary',
                                      'run_job__error_details')

        if len(outputs) > 0:
            percentage_increment = 70.00 / len(outputs)
        else:
            percentage_increment = 0
        completed = 0.0

        with TemporaryDirectory() as td:
            tmp_dir = os.path.join(td, rp_id)  # because rp_id will be name of the packaged zip
            bag = BagIt(tmp_dir)

            for output in outputs:
                j_name = output['run_job__job_name'].split('.')[-1]
                opt_name = output['output_port_type_name']
                rj_uuid = output['run_job__uuid'].hex[0:6]
                op_dir = os.path.join(tmp_dir, "{0}_{1}_{2}".format(j_name, opt_name, rj_uuid))

                rj_status = output['run_job__status']
                if rj_status == task_status.FINISHED:
                    filepath = output['resource__compat_resource_file']
                    ext = os.path.splitext(filepath)[1]
                    result_filename = "{0}_{1}{2}".format(output['resource__name'], output['resource__uuid'].hex[0:6], ext)
                    if not os.path.exists(op_dir):
                        os.makedirs(op_dir)
                    shutil.copyfile(filepath, os.path.join(op_dir, result_filename))
                elif include_failed_runjobs and rj.status == task_status.FAILED:
                    result_filename = "error_{0}_{1}.txt".format(output['resource__name'], output['resource__uuid'].hex[0:6])
                    if not os.path.exists(op_dir):
                        os.makedirs(op_dir)
                    with open(os.path.join(op_dir, result_filename), 'w') as f:
                        f.write("Error Summary: ")
                        f.write(output['run_job__error_summary'])
                        f.write("\n\nError Details:\n")
                        f.write(output['run_job__error_details'])

                completed += percentage_increment
                rp_query.update(percent_completed=int(completed))

            #print [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(tmp_dir)) for f in fn]   # DEBUG
            bag.update()
            errors = bag.validate()
            if not bag.is_valid:
                rp_query.update(status=task_status.FAILED,
                                error_summary="The bag failed validation.",
                                error_details=str(errors))

            target_dir_name = os.path.dirname(package_path)
            if not os.path.isdir(target_dir_name):
                os.mkdir(target_dir_name)
            bag.package(target_dir_name, method='zip')


        rp_query.update(status=task_status.FINISHED,
                        percent_completed=100)
        expiry_time = rp_query.values_list('expiry_time', flat=True)[0]
        if expiry_time:
            async_task = registry.tasks['rodan.core.expire_package'].apply_async((rp_id, ), eta=expiry_time)
            expire_task_id = async_task.task_id
        else:
            expire_task_id = None

        rp_query.update(celery_task_id=expire_task_id)
        return True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        rp_id = args[0]
        rp_query = ResultsPackage.objects.filter(uuid=rp_id)
        rp_query.update(status=task_status.FAILED,
                        error_summary="{0}: {1}".format(type(exc).__name__, str(exc)),
                        error_details=einfo.traceback,
                        celery_task_id=None)

class expire_package(Task):
    name = "rodan.core.expire_package"

    def run(self, rp_id):
        rp_query = ResultsPackage.objects.filter(uuid=rp_id)
        package_path = get_package_path(rp_id)
        os.remove(package_path)
        rp_query.update(status=task_status.EXPIRED, celery_task_id=None)
        return True
