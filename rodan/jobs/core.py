import os
import tempfile
import shutil
import traceback
from pybagit.bagit import BagIt
from celery import task
from django.core.files import File
from django.conf import settings
import PIL.Image
import PIL.ImageFile
from rodan.models import Resource, ResourceType, ResultsPackage
from rodan.models.resultspackage import get_package_path
from rodan.constants import task_status
from celery import Task
from rodan.jobs.base import RodanAutomaticTask

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
        new_processing_status = task_status.FINISHED
        # [TODO] write them into try..except..else..finally..
        if mimetype.startswith('image'):
            from rodan.jobs.conversion.to_png import to_png
            self._task_instance = to_png()
            self._task_instance.run_my_task(inputs, [], outputs)
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
        shutil.rmtree(self._tmpdir)
        del self._tmpdir
        del self._task_instance
        return True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        resource_id = args[0]
        update = self._task_instance._add_error_information_to_runjob(exc, einfo)
        update['processing_status'] = task_status.FAILED
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

@task(name="rodan.core.package_results")
def package_results(rp_id, include_failed_runjobs=False):
    rp_query = ResultsPackage.objects.filter(uuid=rp_id)
    rp_query.update(status=task_status.PROCESSING, celery_task_id=package_results.request.id)
    package_path = get_package_path(rp_id)

    outputs = rp_query.values('output_ports__label',
                              'output_ports__workflow_job__uuid',
                              'output_ports__workflow_job__job__job_name',
                              'output_ports__outputs__resource__uuid',
                              'output_ports__outputs__resource__name',
                              'output_ports__outputs__resource__compat_resource_file',
                              'output_ports__outputs__run_job__status',
                              'output_ports__outputs__run_job__error_summary',
                              'output_ports__outputs__run_job__error_details')

    if len(outputs) > 0:
        percentage_increment = 70.00 / len(outputs)
    else:
        percentage_increment = 0
    completed = 0.0

    try:
        tmp_dir = os.path.join(tempfile.mkdtemp(), rp_id)  # rp_id will be name of the packaged zip
        bag = BagIt(tmp_dir)

        for output in outputs:
            wfj_name = output['output_ports__workflow_job__job__job_name'].split('.')[-1]
            op_label = output['output_ports__label']
            wfj_uuid = output['output_ports__workflow_job__uuid'].hex[0:6]
            op_dir = os.path.join(tmp_dir, "{0}_{1}_{2}".format(wfj_name, op_label, wfj_uuid))

            rj_status = output['output_ports__outputs__run_job__status']
            if rj_status == task_status.FINISHED:
                filepath = output['output_ports__outputs__resource__compat_resource_file']
                ext = os.path.splitext(filepath)[1]
                result_filename = "{0}_{1}{2}".format(output['output_ports__outputs__resource__name'], output['output_ports__outputs__resource__uuid'].hex[0:6], ext)
                if not os.path.exists(op_dir):
                    os.makedirs(op_dir)
                shutil.copyfile(filepath, os.path.join(op_dir, result_filename))
            elif include_failed_runjobs and rj.status == task_status.FAILED:
                result_filename = "error_{0}_{1}.txt".format(output['output_ports__outputs__resource__name'], output['output_ports__outputs__resource__uuid'].hex[0:6])
                if not os.path.exists(op_dir):
                    os.makedirs(op_dir)
                with open(os.path.join(op_dir, result_filename), 'w') as f:
                    f.write("Error Summary: ")
                    f.write(output['output_ports__outputs__run_job__error_summary'])
                    f.write("\n\nError Details:\n")
                    f.write(output['output_ports__outputs__run_job__error_details'])

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
    except Exception as e:
        rp_query.update(status=task_status.FAILED,
                        error_summary=str(e),
                        error_details=traceback.format_exc())
        success = False
    else:
        rp_query.update(status=task_status.FINISHED,
                        percent_completed=100)
        expiry_time = rp_query.values_list('expiry_time', flat=True)[0]
        if expiry_time:
            async_task = expire_package.apply_async((rp_id, ), eta=expiry_time)
            expire_task_id = async_task.task_id
        else:
            expire_task_id = None
        rp_query.update(celery_task_id=expire_task_id)
        success = True
    finally:
        shutil.rmtree(tmp_dir)

    return success


@task(name="rodan.core.expire_package")
def expire_package(rp_id):
    rp_query = ResultsPackage.objects.filter(uuid=rp_id)
    package_path = get_package_path(rp_id)
    try:
        os.remove(package_path)
    except Exception as e:
        return False
    else:
        rp_query.update(status=task_status.EXPIRED, celery_task_id=None)
        return True
