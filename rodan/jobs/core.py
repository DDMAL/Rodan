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
from rodan.models import Resource, ResourceType, ResultsPackage, Output, Workflow, WorkflowRun, WorkflowJob, InputPort, Input, OutputPort, Output, Connection, RunJob
from rodan.models.resultspackage import get_package_path
from rodan.constants import task_status
from celery import Task
from celery.task.control import revoke
from rodan.jobs.base import RodanTask, TemporaryDirectory
from diva_generate_json import GenerateJson
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
import json

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
                self._task.run_my_task(inputs, {}, outputs)
                resource_query.update(resource_type=ResourceType.cached("image/rgb+png").uuid)
                publish_message(Resource, resource_id)
            else:
                shutil.copy(infile_path, tmpfile)
                try:
                    resource_query.update(resource_type=ResourceType.cached(claimed_mimetype).uuid)
                except:
                    resource_query.update(resource_type=ResourceType.cached("application/octet-stream").uuid)
                new_processing_status = task_status.NOT_APPLICABLE

            with open(tmpfile, 'rb') as f:
                resource_object = resource_query[0]
                resource_object.compat_resource_file.save("", File(f), save=False)  # We give an arbitrary name as Django will automatically find the compat_path and extension according to upload_to and resource_type
                compat_resource_file_path = resource_object.compat_resource_file.path
                resource_query.update(compat_resource_file=compat_resource_file_path)
                publish_message(Resource, resource_id)

                if not settings.WITH_DIVA:
                    registry.tasks['rodan.core.create_thumbnails'].run(resource_id) # call synchronously
                else:
                    registry.tasks['rodan.core.create_diva'].run(resource_id) # call synchronously
                resource_query.update(processing_status=new_processing_status)
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
        publish_message(Resource, resource_id)
        return True
    else:
        return False


# if WITH_DIVA set, try to import the executables kdu_compress and convert.
if getattr(settings, 'WITH_DIVA'):
    from distutils.spawn import find_executable

    BIN_KDU_COMPRESS = getattr(settings, 'BIN_KDU_COMPRESS', None) or find_executable('kdu_compress')
    if not BIN_KDU_COMPRESS:
        raise ImportError("cannot find kdu_compress")

    BIN_CONVERT = getattr(settings, 'BIN_CONVERT', None) or find_executable('convert')
    if not BIN_CONVERT:
        raise ImportError("cannot find convert")


@task(name="rodan.core.create_diva")
def create_diva(resource_id):
    if not getattr(settings, 'WITH_DIVA'):
        return False

    resource_query = Resource.objects.filter(uuid=resource_id).select_related('resource_type')
    resource_object = resource_query[0]
    mimetype = resource_object.resource_type.mimetype

    if not os.path.exists(resource_object.diva_path):
        os.makedirs(resource_object.diva_path)

    if mimetype.startswith('image'):
        inputs = {'in': [{
            'resource_path': resource_object.compat_resource_file.path,
            'resource_type': mimetype
        }]}
        outputs = {'out': [{
            'resource_path': resource_object.diva_jp2_path,
            'resource_type': 'image/jp2'
        }]}

        _task = registry.tasks['rodan.jobs.conversion.to_jpeg2000']
        _task.run_my_task(inputs, {}, outputs)

        gen = GenerateJson(input_directory=resource_object.diva_path,
                           output_directory=resource_object.diva_path)
        gen.title = 'measurement'
        gen.generate()

        resource_query.update(has_thumb=True)
        publish_message(Resource, resource_id)
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

                        res_name = res_namefinder.find(output['run_job__resource_uuid'], output['resource__name'])  # [TODO]: or... find the modified resource name if the resource_uuid still exists?
                        result_filename = "{0}{1}".format(res_name, ext)
                        if not os.path.exists(op_dir):
                            os.makedirs(op_dir)
                        shutil.copyfile(filepath, os.path.join(op_dir, result_filename))

                elif mode == 1:
                    res_name = res_namefinder.find(output['run_job__resource_uuid'], output['resource__name'])  # [TODO]: or... find the modified resource name if the resource_uuid still exists?
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
            self.new_name_pattern = new_name_pattern
        def find(self, identifier, original_name):
            if identifier not in self.id_name_map:
                if original_name not in self.original_name_count:
                    self.original_name_count[original_name] = 1
                    self.id_name_map[identifier] = original_name
                    return original_name
                else:
                    self.original_name_count[original_name] += 1
                    new_name = self.new_name_pattern.format(original_name, self.original_name_count[original_name])
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



class create_workflowrun(Task):
    """
    Called by WorkflowRun create view. Given the Workflow, create Inputs, Outputs,
    and RunJobs in the newly-created WorkflowRun, and start the WorkflowRun.
    """

    name = 'rodan.core.create_workflowrun'

    def run(self, wf_id, wfrun_id, resource_assignment_dict):
        workflow = Workflow.objects.get(uuid=wf_id)
        workflow_run = WorkflowRun.objects.get(uuid=wfrun_id)

        endpoint_workflowjobs = self._endpoint_workflow_jobs(workflow)
        singleton_workflowjobs = self._singleton_workflow_jobs(workflow, resource_assignment_dict)
        workflowjob_runjob_map = {}
        output_outputport_map = {}
        outputportrunjob_output_map = {}

        def create_runjob_A(wfjob, arg_resource):
            run_job = RunJob(workflow_job=wfjob,
                             workflow_job_uuid=wfjob.uuid.hex,
                             resource_uuid=arg_resource.uuid.hex if arg_resource else None,
                             workflow_run=workflow_run,
                             job_name=wfjob.job.name,
                             job_settings=wfjob.job_settings)
            run_job.save()

            outputports = OutputPort.objects.filter(workflow_job=wfjob).prefetch_related('output_port_type__resource_types')

            for op in outputports:
                resource = Resource(project=workflow_run.workflow.project,
                                    resource_type=ResourceType.cached('application/octet-stream'))  # ResourceType will be determined later (see method _create_runjobs)
                resource.save()

                output = Output(output_port=op,
                                run_job=run_job,
                                resource=resource,
                                output_port_type_name=op.output_port_type.name)
                output.save()

                resource.description = """Generated by workflow {0}. Output of {1}:{2}""".format(workflow_run.name, run_job.job_name, output.output_port_type_name)   # [TODO] could be better described.
                if arg_resource:   # which resource in multiple resources?
                    resource.name = arg_resource.name
                else:
                    resource.name = 'Output of workflow {0}'.format(workflow_run.name)  # assign a name for it
                resource.origin = output
                resource.save()

                output_outputport_map[output] = op
                outputportrunjob_output_map[(op, run_job)] = output

            return run_job


        def create_runjobs(wfjob_A, arg_resource):
            if wfjob_A in workflowjob_runjob_map:
                return workflowjob_runjob_map[wfjob_A]

            runjob_A = create_runjob_A(wfjob_A, arg_resource)

            incoming_connections = Connection.objects.filter(input_port__workflow_job=wfjob_A)

            for conn in incoming_connections:
                wfjob_B = conn.output_workflow_job
                runjob_B = create_runjobs(wfjob_B, arg_resource)

                associated_output = outputportrunjob_output_map[(conn.output_port, runjob_B)]

                Input(run_job=runjob_A,
                      input_port=conn.input_port,
                      input_port_type_name=conn.input_port.input_port_type.name,
                      resource=associated_output.resource).save()

            # entry inputs
            for wfj_ip in wfjob_A.input_ports.all():
                if wfj_ip in resource_assignment_dict:
                    ress = resource_assignment_dict[wfj_ip]
                    if len(ress) > 1:
                        entry_res = arg_resource
                    else:
                        entry_res = ress[0]

                    Input(run_job=runjob_A,
                          input_port=wfj_ip,
                          input_port_type_name=wfj_ip.input_port_type.name,
                          resource=entry_res).save()

            # Determine ResourceType of the outputs of RunJob A.
            for o in runjob_A.outputs.all():
                resource_type_set = set(o.output_port.output_port_type.resource_types.all())
                res = o.resource

                if len(resource_type_set) > 1:
                    ## Eliminate this set by considering the connected InputPorts
                    for connection in o.output_port.connections.all():
                        in_type_set = set(connection.input_port.input_port_type.resource_types.all())
                        resource_type_set.intersection_update(in_type_set)

                if len(resource_type_set) > 1:
                    ## Try to find a same resource type in the input resources.
                    for i in runjob_A.inputs.all():
                        if i.resource.resource_type in resource_type_set:
                            res.resource_type = i.resource.resource_type
                            break
                    else:
                        res.resource_type = resource_type_set.pop()
                else:
                    res.resource_type = resource_type_set.pop()
                res.save()

            workflowjob_runjob_map[wfjob_A] = runjob_A
            return runjob_A


        def runjob_creation_loop(arg_resource):
            for wfjob in endpoint_workflowjobs:
                create_runjobs(wfjob, arg_resource)

            workflow_job_iteration = {}

            for wfjob in workflowjob_runjob_map:
                workflow_job_iteration[wfjob] = workflowjob_runjob_map[wfjob]

            for wfjob in workflow_job_iteration:
                if wfjob not in singleton_workflowjobs:
                    del workflowjob_runjob_map[wfjob]


        # Main:
        ress_multiple = None
        for ip, ress in resource_assignment_dict.iteritems():
            if len(ress) > 1:
                ress_multiple = ress
                break

        if ress_multiple:
            for res in ress_multiple:
                runjob_creation_loop(res)
        else:
            runjob_creation_loop(None)

        ## call master_task
        registry.tasks['rodan.core.master_task'].apply_async((wfrun_id,))

    def _endpoint_workflow_jobs(self, workflow):
        workflow_jobs = WorkflowJob.objects.filter(workflow=workflow)
        endpoint_workflowjobs = []

        for wfjob in workflow_jobs:
            connections = Connection.objects.filter(output_port__workflow_job=wfjob)

            if not connections:
                endpoint_workflowjobs.append(wfjob)

        return endpoint_workflowjobs

    def _singleton_workflow_jobs(self, workflow, resource_assignment_dict):
        singleton_workflowjobs = []

        def traversal(wfjob):
            if wfjob in singleton_workflowjobs:
                singleton_workflowjobs.remove(wfjob)
            adjacent_connections = Connection.objects.filter(output_port__workflow_job=wfjob)
            for conn in adjacent_connections:
                adj_wfjob = WorkflowJob.objects.get(input_ports=conn.input_port)
                traversal(adj_wfjob)

        for wfjob in WorkflowJob.objects.filter(workflow=workflow):
            singleton_workflowjobs.append(wfjob)

        for ip, ress in resource_assignment_dict.iteritems():
            if len(ress) > 1:
                initial_wfjob = ip.workflow_job
                traversal(initial_wfjob)

        return singleton_workflowjobs


@task(name="rodan.core.cancel_workflowrun")
def cancel_workflowrun(wfrun_id):
    wfrun = WorkflowRun.objects.get(uuid=wfrun_id)
    runjobs_to_revoke_query = RunJob.objects.filter(workflow_run=wfrun, status__in=(task_status.SCHEDULED, task_status.PROCESSING, task_status.WAITING_FOR_INPUT))
    runjobs_to_revoke_celery_id = runjobs_to_revoke_query.values_list('celery_task_id', flat=True)
    for celery_id in runjobs_to_revoke_celery_id:
        if celery_id is not None:
            revoke(celery_id, terminate=True)
    runjobs_to_revoke_query.update(status=task_status.CANCELLED)
    publish_message(WorkflowRun, wfrun_id)

@task(name="rodan.core.retry_workflowrun")
def retry_workflowrun(wfrun_id):
    wfrun = WorkflowRun.objects.get(uuid=wfrun_id)
    runjobs_to_retry_query = RunJob.objects.filter(workflow_run=wfrun, status__in=(task_status.FAILED, task_status.CANCELLED))
    for rj in runjobs_to_retry_query:
        rj.status = task_status.SCHEDULED
        rj.error_summary = ''
        rj.error_details = ''
        original_settings = {}
        for k, v in rj.job_settings.iteritems():
            if not k.startswith('@'):
                original_settings[k] = v
        rj.job_settings = original_settings
        rj.save(update_fields=['status', 'job_settings', 'error_summary', 'error_details'])

    registry.tasks['rodan.core.master_task'].apply_async((wfrun_id,))

def publish_message(model, uuid):
    publisher = RedisPublisher(facility='rodan', broadcast=True)
    data = {"status": "updated", "model": model.__name__, "uuid": "{0}".format(uuid)}
    message = RedisMessage(json.dumps(data))
    publisher.publish_message(message)
