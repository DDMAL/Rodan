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
from rodan.jobs.base import RodanTask, TemporaryDirectory

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

    def run(self, rp_id):
        rp_query = ResultsPackage.objects.filter(uuid=rp_id)
        rp_query.update(status=task_status.PROCESSING, celery_task_id=self.request.id)
        rp = rp_query.first()
        mode = rp.packaging_mode
        package_path = get_package_path(rp_id)

        if mode == 0:
            # Get endpoint outputs
            output_query = Output.objects.filter(Q(run_job__workflow_run=rp.workflow_run) &
                                                 (Q(resource__inputs__isnull=True) | ~Q(resource__inputs__run_job__workflow_run=rp.workflow_run)))
        else:
            # Get all outputs
            output_query = Output.objects.filter(Q(run_job__workflow_run=rp.workflow_run))
        outputs = output_query.values('output_port_type_name',
                                      'run_job__workflow_job_uuid',
                                      'run_job__resource_uuid',
                                      'run_job__job_name',
                                      'resource__name',
                                      'resource__compat_resource_file',
                                      'run_job__status',
                                      'run_job__job_settings',
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

            job_namefinder = self._NameFinder()
            res_namefinder = self._NameFinder()

            for output in outputs:
                if mode == 0:  # only endpoint resources, subdirectoried by different outputs
                    j_name = job_namefinder.find(output['run_job__workflow_job_uuid'], output['run_job__job_name'])
                    opt_name = output['output_port_type_name']
                    op_dir = os.path.join(tmp_dir, "{0} - {1}".format(j_name, opt_name))

                    rj_status = output['run_job__status']
                    if rj_status == task_status.FINISHED:
                        filepath = output['resource__compat_resource_file']
                        ext = os.path.splitext(filepath)[1]

                        res_name = res_namefinder.find(output['run_job__resource_uuid'], output['resource__name'])
                        result_filename = "{0}{1}".format(res_name, ext)
                        if not os.path.exists(op_dir):
                            os.makedirs(op_dir)
                        shutil.copyfile(filepath, os.path.join(op_dir, result_filename))

                elif mode == 1:
                    res_name = res_namefinder.find(output['run_job__resource_uuid'], output['resource__name'])
                    res_dir = os.path.join(tmp_dir, res_name)

                    j_name = job_namefinder.find(output['run_job__workflow_job_uuid'], output['run_job__job_name'])
                    opt_name = output['output_port_type_name']

                    rj_status = output['run_job__status']
                    if rj_status == task_status.FINISHED:
                        filepath = output['resource__compat_resource_file']
                        ext = os.path.splitext(filepath)[1]
                        result_filename = "{0} - {1}{2}".format(j_name, opt_name, ext)
                        if not os.path.exists(res_dir):
                            os.makedirs(res_dir)
                        shutil.copyfile(filepath, os.path.join(res_dir, result_filename))
                    elif rj_status == task_status.FAILED:
                        result_filename = "{0} - {1} - ERROR.txt".format(j_name, opt_name)
                        if not os.path.exists(res_dir):
                            os.makedirs(res_dir)
                        with open(os.path.join(res_dir, result_filename), 'w') as f:
                            f.write("Error Summary: ")
                            f.write(output['run_job__error_summary'])
                            f.write("\n\nError Details:\n")
                            f.write(output['run_job__error_details'])
                elif mode == 2:
                    raise NotImplementedError() # [TODO]
                else:
                    raise ValueError("mode {0} is not supported".format(mode))

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
                os.makedirs(target_dir_name)
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

    class _NameFinder(object):
        """
        Find a name given unique identifier and a preferred original name.
        """
        def __init__(self, new_name_pattern="{0} ({1})"):
            self.original_name_count = {}
            self.id_name_map = {}
        def find(self, identifier, original_name):
            if identifier not in self.id_name_map:
                if original_name not in self.original_name_count:
                    self.original_name_count[original_name] = 1
                    self.id_name_map[identifier] = original_name
                    return original_name
                else:
                    self.original_name_count[original_name] += 1
                    new_name = new_name_pattern.format(original_name, self.original_name_count[original_name])
                    self.id_name_map[identifier] = new_name
                    return new_name
            else:
                return self.id_name_map[identifier]

class expire_package(Task):
    name = "rodan.core.expire_package"

    def run(self, rp_id):
        rp_query = ResultsPackage.objects.filter(uuid=rp_id)
        package_path = get_package_path(rp_id)
        os.remove(package_path)
        rp_query.update(status=task_status.EXPIRED, celery_task_id=None)
        return True
