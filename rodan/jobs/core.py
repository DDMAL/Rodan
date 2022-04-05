from __future__ import absolute_import

from collections import OrderedDict
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

from celery import task, registry
from celery import Task
from celery.task.control import revoke
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Case, Value, When, BooleanField
import PIL
from pybagit.bagit import BagIt
import six

import rodan  # noqa
from rodan.models import (
    Resource,
    ResourceType,
    ResultsPackage,
    Workflow,
    WorkflowRun,
    WorkflowJob,
    InputPort,
    Input,
    OutputPort,
    Output,
    Connection,
    RunJob,
    ResourceList,
)
from rodan.models.resultspackage import get_package_path
from rodan.constants import task_status
from rodan.jobs.base import TemporaryDirectory
from rodan.jobs.diva_generate_json import GenerateJson
from rodan.jobs.resource_identification import fileparse

# from rodan.celery import app


class create_resource(Task):
    name = "rodan.core.create_resource"
    queue = "celery"

    def run(self, resource_id, claimed_mimetype=None):
        resource_query = Resource.objects.filter(uuid=resource_id)
        resource_query.update(processing_status=task_status.PROCESSING)
        resource_info = resource_query.values("resource_type__mimetype", "resource_file")[0]

        with TemporaryDirectory() as tmpdir:
            infile_path = resource_info["resource_file"]
            tmpfile = os.path.join(tmpdir, "temp")

            if claimed_mimetype == "application/octet-stream":
                mimetype = fileparse(infile_path)
            else:
                mimetype = claimed_mimetype

            inputs = {"in": [{"resource_path": infile_path, "resource_type": mimetype}]}  # noqa
            outputs = {"out": [{"resource_path": tmpfile, "resource_type": ""}]}  # noqa

            new_processing_status = task_status.FINISHED

            shutil.copy(infile_path, tmpfile)

            try:
                resource_query.update(
                    resource_type=ResourceType.objects.get(mimetype=mimetype)
                )
            except ObjectDoesNotExist:
                resource_query.update(
                    resource_type=ResourceType.objects.get(
                        mimetype="application/octet-stream"
                    )
                )
            new_processing_status = task_status.NOT_APPLICABLE

            if mimetype.startswith("image"):
                registry.tasks["rodan.core.create_diva"].si(resource_id).apply_async(queue="celery")

            resource_query.update(processing_status=new_processing_status)
        return True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        resource_id = args[0]
        resource_query = Resource.objects.filter(uuid=resource_id)

        if hasattr(self, "_task"):
            update = self._task._add_error_information_to_runjob(exc, einfo)
            update["processing_status"] = task_status.FAILED
            resource_query.update(**update)
            del self._task
        else:
            resource_query.update(
                processing_status=task_status.FAILED,
                error_summary="{0}: {1}".format(type(exc).__name__, str(exc)),
                error_details=einfo.traceback,
            )

# class test_task(Task):
#     name = "rodan.core.test_task"
#     queue = "celery"

# @task(name="rodan.core.create_thumbnails")
# def create_thumbnails(resource_id):
#     resource_query = Resource.objects.filter(uuid=resource_id).select_related('resource_type')
#     resource_object = resource_query[0]
#     mimetype = resource_object.resource_type.mimetype
#
#     if mimetype.startswith('image'):
#         image = PIL.Image.open(resource_object.resource_file.path).convert('RGB')
#         width = float(image.size[0])
#         height = float(image.size[1])
#
#         for thumbnail_size in settings.THUMBNAIL_SIZES:
#             thumbnail_size = float(thumbnail_size)
#             ratio = min((thumbnail_size / width), (thumbnail_size / height))
#             dimensions = (int(width * ratio), int(height * ratio))
#
#             thumbnail_size = str(int(thumbnail_size))
#             thumb_copy = image.resize(dimensions, PIL.Image.ANTIALIAS)
#             thumb_copy.save(os.path.join(resource_object.thumb_path,
#                                          resource_object.thumb_filename(size=thumbnail_size)))
#
#             del thumb_copy
#         del image
#         resource_query.update(has_thumb=True)
#         return True
#     else:
#         return False


# if ENABLE_DIVA set, try to import the executables kdu_compress and convert.
if getattr(settings, "ENABLE_DIVA"):
    from distutils.spawn import find_executable

    BIN_GM = getattr(settings, "BIN_GM", None) or find_executable("gm")
    if not BIN_GM:
        raise ImportError("cannot find gm")


@task(name="rodan.core.create_diva")
def create_diva(resource_id):
    """
    This celery task creates the DIVA folder and a JPEG2000 image within it.

    The created JPEG2000 file is for viewing purposes inside of IIPSRV only.
    This JPEG2000 file is NOT used for analysis or other Rodan jobs.

    To enable JPEG2000 in Python Pillow you need to install OpenJPEG anyway.
        https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-2000

    There is a colour profile issue that stops us from using OpenJPEG directly. For this reason, we
    are using Grok to create the JPEG2000 for IIPSRV with the right colour profile.
    """
    # TODO: Move to only use python Pillow or CV2.
    # TODO: Remove GraphicsMagick completely.

    # BUG: The shutil command occasionally get's a `IOError: [Errno 2] No such file or directory`
    # Can not reliably trigger this error. It's some sort of race condition, maybe struggling
    # to figure out which job creates the resource folder? It happens very rarely.
    #
    #   1) Did kakadu finish converting the file?
    #   2) Does the folder exist?
    #
    # try:
    #     shutil.move(name + ".jp2", outputs['JPEG2000 Image'][0]['resource_path'])
    # except IOError:
    #     os.makedirs(outputs['JPEG2000 Image'][0]['resource_path'])
    #     shutil.move(name + ".jp2", outputs['JPEG2000 Image'][0]['resource_path'])
    #
    # if not os.path.exists(outputs['JPEG2000 Image'][0]['resource_path']):
    #     os.makedirs(outputs['JPEG2000 Image'][0]['resource_path'])
    #     shutil.move(name + ".jp2", outputs['JPEG2000 Image'][0]['resource_path'])

    if not getattr(settings, "ENABLE_DIVA"):
        return False

    resource_query = Resource.objects.filter(uuid=resource_id).select_related(
        "resource_type"
    )
    resource_object = resource_query[0]
    mimetype = resource_object.resource_type.mimetype

    if not os.path.exists(resource_object.diva_path):
        os.makedirs(resource_object.diva_path)

    inputs = {
        "Image": [
            {
                "resource_path": resource_object.resource_file.path,
                "resource_type": mimetype,
            }
        ]
    }
    outputs = {
        "JPEG2000 Image": [
            {
                "resource_path": resource_object.diva_jp2_path,
                "resource_type": "image/jp2",
            }
        ]
    }

    with tempfile.NamedTemporaryFile(suffix=".tiff") as tmp_file:

        name = os.path.basename(tmp_file.name)
        name, ext = os.path.splitext(name)

        # Files
        tiff_file = tmp_file.name
        jp2_file = "/tmp/" + name + ".jp2"  # same file with a different extension

        # subprocess.check_call(
        #     args=[
        #         BIN_GM,
        #         "convert",
        #         "-depth", "8",  # output RGB
        #         "-compress", "None",
        #         # image file input
        #         inputs["Image"][0]["resource_path"],
        #         tiff_file  # tiff file output
        #     ]
        # )
        im = PIL.Image.open(inputs["Image"][0]["resource_path"])
        rgb_im = im.convert("RGB")
        rgb_im.save(tiff_file)

        # Kakadu and OpenJPEG can only convert certain file formats.
        # Tiff is one of those formats.
        # This means we can convert to JPEG2000 for IIPSRV after converting the
        # original to tiff.
        subprocess.check_call(
            args=[
                # With Grok + OpenJPEG  # noqa
                "/vendor/grok/build/bin/grk_compress",
                "-i", tiff_file,
                "-o", jp2_file,
                "-n", "5",
                "-c", "[256,256],[256,256],[128,128]",
                "-SOP",
                "-p", "LRCP",
                "-r", "16,8,4,2"
            ]
        )

    shutil.move(jp2_file, outputs['JPEG2000 Image'][0]['resource_path'])

    gen = GenerateJson(
        input_directory=resource_object.diva_path,
        output_directory=resource_object.diva_path,
    )
    gen.title = "measurement"
    gen.generate()
    # resource_query.update(has_thumb=True)
    return True


class package_results(Task):
    # [TODO] this code needs refactoring. It should be possible to parameterize this
    # core job in some way according to user needs...
    name = "rodan.core.package_results"
    queue = "celery"

    def run(self, rp_id):
        rp_query = ResultsPackage.objects.filter(uuid=rp_id)
        rp_query.update(status=task_status.PROCESSING, celery_task_id=self.request.id)
        rp = rp_query.first()
        mode = rp.packaging_mode
        package_path = get_package_path(rp_id)

        output_objs = (
            Output.objects.filter(run_job__workflow_run=rp.workflow_run)
            .select_related(
                "resource", "resource__resource_type", "resource_list", "run_job"
            )
            .prefetch_related("resource_list__resources")
            .annotate(
                is_endpoint=Case(
                    When(
                        condition=(
                            Q(resource__isnull=False)
                            & (
                                Q(resource__inputs__isnull=True)
                                | ~Q(
                                    resource__inputs__run_job__workflow_run=rp.workflow_run
                                )
                            )
                        )
                        | (
                            Q(resource_list__isnull=False)
                            & (
                                Q(resource_list__inputs__isnull=True)
                                | ~Q(
                                    resource_list__inputs__run_job__workflow_run=rp.workflow_run
                                )
                            )
                        ),
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        )

        if len(output_objs) > 0:
            percentage_increment = 70.00 / len(output_objs)
        else:
            percentage_increment = 0
        completed = 0.0

        with TemporaryDirectory() as td:
            tmp_dir = os.path.join(
                td, rp_id
            )  # because rp_id will be name of the packaged zip
            bag = BagIt(tmp_dir)

            job_namefinder = self._NameFinder()
            res_namefinder = self._NameFinder()

            for output in output_objs:
                if mode == 0:
                    # only endpoint resources, subdirectoried by different outputs
                    # continue if not endpoint output
                    if output.is_endpoint is False:
                        continue

                    j_name = job_namefinder.find(
                        output.run_job.workflow_job_id, output.run_job.job_name
                    )
                    opt_name = output.output_port_type_name
                    op_dir = os.path.join(tmp_dir, "{0} - {1}".format(j_name, opt_name))

                    rj_status = output.run_job.status
                    if rj_status == task_status.FINISHED:
                        if output.resource is not None:
                            filepath = output.resource.resource_file.path
                            ext = os.path.splitext(filepath)[1]
                            # [TODO]: or... find the modified resource name if
                            # the resource_uuid still exists?
                            res_name = res_namefinder.find(
                                output.resource_id,
                                output.resource.name
                            )
                            result_filename = "{0}{1}".format(res_name, ext)
                            if not os.path.exists(op_dir):
                                os.makedirs(op_dir)
                            shutil.copyfile(
                                filepath, os.path.join(op_dir, result_filename)
                            )
                        elif output.resource_list is not None:
                            # [TODO]: or... find the modified resource name if the
                            # resource_uuid still exists?
                            res_name = res_namefinder.find(
                                output.resource_list_id,
                                output.resource_list.name
                            )
                            result_foldername = "{0}.list".format(res_name)
                            result_folder = os.path.join(op_dir, result_foldername)
                            if not os.path.exists(result_folder):
                                os.makedirs(result_folder)

                            cnt = output.resource_list.resources.count()
                            zfills = len(str(cnt))
                            for idx, r in enumerate(
                                output.resource_list.resources.all()
                            ):
                                filepath = r.resource_file.path
                                ext = os.path.splitext(filepath)[1]
                                new_filename = "{0}{1}".format(
                                    str(idx).zfill(zfills), ext
                                )
                                shutil.copyfile(
                                    filepath, os.path.join(result_folder, new_filename)
                                )

                elif mode == 1:
                    # [TODO]: or... find the modified resource name if the resource_uuid still
                    # exists?
                    res_name = res_namefinder.find(output.resource_id, output.resource.name)
                    res_dir = os.path.join(tmp_dir, res_name)

                    j_name = job_namefinder.find(
                        output.run_job.workflow_job_id, output.run_job.job_name
                    )
                    opt_name = output.output_port_type_name

                    rj_status = output.run_job.status
                    if rj_status == task_status.FINISHED:
                        if output.resource is not None:
                            filepath = output.resource.resource_file.path
                            ext = os.path.splitext(filepath)[1]
                            result_filename = "{0} - {1}{2}".format(
                                j_name, opt_name, ext
                            )
                            if not os.path.exists(res_dir):
                                os.makedirs(res_dir)
                            shutil.copyfile(
                                filepath, os.path.join(res_dir, result_filename)
                            )
                        elif output.resource_list is not None:
                            result_foldername = "{0} - {1}.list".format(
                                j_name, opt_name
                            )
                            result_folder = os.path.join(res_dir, result_foldername)
                            if not os.path.exists(result_folder):
                                os.makedirs(result_folder)

                            cnt = output.resource_list.resources.count()
                            zfills = len(str(cnt))
                            for idx, r in enumerate(
                                output.resource_list.resources.all()
                            ):
                                filepath = r.resource_file.path
                                ext = os.path.splitext(filepath)[1]
                                new_filename = "{0}{1}".format(
                                    str(idx).zfill(zfills), ext
                                )
                                shutil.copyfile(
                                    filepath, os.path.join(result_folder, new_filename)
                                )

                    elif rj_status == task_status.FAILED:
                        result_filename = "{0} - {1} - ERROR.txt".format(
                            j_name, opt_name
                        )
                        if not os.path.exists(res_dir):
                            os.makedirs(res_dir)
                        with open(os.path.join(res_dir, result_filename), "w") as f:
                            f.write("Error Summary: ")
                            f.write(output.run_job.error_summary)
                            f.write("\n\nError Details:\n")
                            f.write(output.run_job.error_details)
                elif mode == 2:
                    raise NotImplementedError()  # [TODO]
                else:
                    raise ValueError("mode {0} is not supported".format(mode))

                completed += percentage_increment
                rp_query.update(percent_completed=int(completed))

            # DEBUG
            # print([os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(tmp_dir)) for f in fn])  # noqa
            bag.update()
            errors = bag.validate()
            if not bag.is_valid:
                rp_query.update(
                    status=task_status.FAILED,
                    error_summary="The bag failed validation.",
                    error_details=str(errors),
                )

            target_dir_name = os.path.dirname(package_path)
            if not os.path.isdir(target_dir_name):
                os.makedirs(target_dir_name)
            bag.package(target_dir_name, method="zip")

        rp_query.update(status=task_status.FINISHED, percent_completed=100)
        expiry_time = rp_query.values_list("expiry_time", flat=True)[0]
        if expiry_time:
            async_task = registry.tasks["rodan.core.expire_package"].apply_async(
                (rp_id,), eta=expiry_time, queue="celery"
            )
            expire_task_id = async_task.task_id
        else:
            expire_task_id = None

        rp_query.update(celery_task_id=expire_task_id)
        return True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        rp_id = args[0]
        rp_query = ResultsPackage.objects.filter(uuid=rp_id)
        rp_query.update(
            status=task_status.FAILED,
            error_summary="{0}: {1}".format(type(exc).__name__, str(exc)),
            error_details=einfo.traceback,
            celery_task_id=None,
        )

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
                    new_name = self.new_name_pattern.format(
                        original_name, self.original_name_count[original_name]
                    )
                    self.id_name_map[identifier] = new_name
                    return new_name
            else:
                return self.id_name_map[identifier]


class expire_package(Task):
    name = "rodan.core.expire_package"
    queue = "celery"

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

    name = "rodan.core.create_workflowrun"
    queue = "celery"

    def run(self, wf_id, wfrun_id, resource_assignment_dict):
        workflow = Workflow.objects.get(uuid=wf_id)
        workflow_run = WorkflowRun.objects.get(uuid=wfrun_id)

        def convert_string_to_model_dict(dict_):
            """
            Passing messages to celery is faster when using JSON, the problem is you are
            limited by types. Pickle objects are insecure and slower, but the fact that we
            are searching for the resource again would slow down things.

            [TODO] Refactor so we don't need to query the database so often, and look
            into the possibility of using YAML (still faster than pickle but has more
            options than JSON. It might be possible to pass a model in yaml and that
            would make be great.)
            """
            temp_dict = {}
            for item in dict_.items():
                if isinstance(item[1], list):
                    try:
                        temp_dict[InputPort.objects.get(uuid=item[0])] = [
                            Resource.objects.get(uuid=x) for x in item[1]
                        ]
                    except Resource.DoesNotExist:
                        temp_dict[InputPort.objects.get(uuid=item[0])] = [
                            ResourceList.objects.get(uuid=x) for x in item[1]
                        ]
                elif isinstance(item[1], str):
                    try:
                        temp_dict[InputPort.objects.get(uuid=item[0])] = Resource.objects.get(
                            uuid=item[1]
                        )
                    except Resource.DoesNotExist:
                        temp_dict[InputPort.objects.get(uuid=item[0])] = ResourceList.objects.get(
                            uuid=item[1]
                        )
                else:
                    raise Exception(
                        "Unusual input to convert_string_to_model_dict: {}".format(dict_)
                    )
            return temp_dict

        resource_assignment_dict = convert_string_to_model_dict(resource_assignment_dict)

        endpoint_workflowjobs = self._endpoint_workflow_jobs(workflow)
        singleton_workflowjobs = self._singleton_workflow_jobs(
            workflow, resource_assignment_dict
        )
        workflowjob_runjob_map = {}
        output_outputport_map = {}
        outputportrunjob_output_map = {}

        def create_runjob_A(wfjob, this_ip_resource_map):
            # Backwords compatibility:
            # RunJob.resource_uuid is used to label which one in the resource collection
            # the RunJob was created from. But this is not depicting the full image when
            # there are multiple resource collections. Therefore, if there's only one
            # resource collection (as we can tell from this_ip_resource_map), we follow
            # the previous way; otherwise, we simply pick the first one from the map.
            if len(this_ip_resource_map.keys()) == 0:
                labelling_resource = None
            else:
                _, labelling_resource = next(iter(this_ip_resource_map.items()))

            run_job = RunJob(
                workflow_job=wfjob,
                workflow_job_uuid=wfjob.uuid.hex,
                resource_uuid=labelling_resource.uuid.hex if labelling_resource else None,
                workflow_run=workflow_run,
                job_name=wfjob.job.name,
                job_settings=wfjob.job_settings,
                job_queue=wfjob.job.job_queue,
            )
            run_job.save()

            outputports = OutputPort.objects.filter(
                workflow_job=wfjob
            ).prefetch_related("output_port_type__resource_types")

            for op in outputports:
                if op.output_port_type.is_list is False:
                    model = Resource
                    arg_name = "resource"
                else:
                    model = ResourceList
                    arg_name = "resource_list"

                r = model(
                    project=workflow_run.workflow.project,
                    resource_type=ResourceType.objects.get(
                        mimetype="application/octet-stream"
                    ),
                )  # ResourceType will be determined later (see method _create_runjobs)
                r.save()

                kwargs = {
                    "output_port": op,
                    "run_job": run_job,
                    arg_name: r,
                    "output_port_type_name": op.output_port_type.name,
                }
                output = Output(**kwargs)
                output.save()

                r.description = """Generated by workflow: {0}-{1} \n workflow_run: {2}-{3} \n job: {4}-{5} \n workflow_job: {6}-{7} \n workflow_job setting: {8} \n run_job: {9}-{10}""".format(  # noqa
                    workflow_run.workflow.name,
                    workflow_run.workflow.uuid,
                    workflow_run.name,
                    workflow_run.uuid,
                    wfjob.job.name,
                    wfjob.job.uuid,
                    wfjob.name,
                    wfjob.uuid,
                    wfjob.job_settings,
                    run_job.job_name,
                    run_job.uuid,
                )
                if labelling_resource:
                    # Same as the comments at the top of this function
                    r.name = labelling_resource.name
                else:
                    r.name = "{0} - {1}".format(
                        wfjob.job.name, output.output_port_type_name
                    )

                r.origin = output
                r.save()

                output_outputport_map[output] = op
                outputportrunjob_output_map[(op, run_job)] = output

            return run_job

        def create_runjobs(wfjob_A, this_ip_resource_map):
            if wfjob_A in workflowjob_runjob_map:
                return workflowjob_runjob_map[wfjob_A]

            runjob_A = create_runjob_A(wfjob_A, this_ip_resource_map)

            incoming_connections = Connection.objects.filter(
                input_port__workflow_job=wfjob_A
            )

            for conn in incoming_connections:
                wfjob_B = conn.output_workflow_job
                runjob_B = create_runjobs(wfjob_B, this_ip_resource_map)

                associated_output = outputportrunjob_output_map[
                    (conn.output_port, runjob_B)
                ]

                if associated_output.resource:
                    Input(
                        run_job=runjob_A,
                        input_port=conn.input_port,
                        input_port_type_name=conn.input_port.input_port_type.name,
                        resource=associated_output.resource,
                    ).save()
                else:
                    Input(
                        run_job=runjob_A,
                        input_port=conn.input_port,
                        input_port_type_name=conn.input_port.input_port_type.name,
                        resource_list=associated_output.resource_list,
                    ).save()
            # entry inputs
            for wfj_ip in wfjob_A.input_ports.all():
                if wfj_ip in resource_assignment_dict:
                    ress = resource_assignment_dict[wfj_ip]
                    if len(ress) > 1:
                        # This InputPort links to a resource collection and we
                        # need to find out the correct resource that we are
                        # working on for this InputPort.
                        entry_res = this_ip_resource_map[wfj_ip]
                    else:
                        # This InputPort does not link to a resource collection
                        entry_res = ress[0]

                    if isinstance(entry_res, Resource):
                        Input(
                            run_job=runjob_A,
                            input_port=wfj_ip,
                            input_port_type_name=wfj_ip.input_port_type.name,
                            resource=entry_res,
                        ).save()
                    else:
                        Input(
                            run_job=runjob_A,
                            input_port=wfj_ip,
                            input_port_type_name=wfj_ip.input_port_type.name,
                            resource_list=entry_res,
                        ).save()

            # Determine ResourceType of the outputs of RunJob A
            for o in runjob_A.outputs.all():
                resource_type_set = set(
                    o.output_port.output_port_type.resource_types.all()
                )
                res = o.resource or o.resource_list

                if type(res) is Resource:
                    # if type(res) is Resource:
                    if len(resource_type_set) > 1:
                        # Eliminate this set by considering the connected InputPorts
                        for connection in o.output_port.connections.all():
                            in_type_set = set(
                                connection.input_port.input_port_type.resource_types.all()
                            )
                            resource_type_set.intersection_update(in_type_set)

                    if len(resource_type_set) > 1:
                        # Try to find a same resource type in the input resources.
                        for i in runjob_A.inputs.all():
                            r = i.resource or i.resource_list
                            if r.resource_type in resource_type_set:
                                res.resource_type = r.resource_type
                                break
                        else:
                            res.resource_type = resource_type_set.pop()
                    else:
                        res.resource_type = resource_type_set.pop()
                    res.save()

            # for o in runjob_A.outputs.all().select_related('output_port__output_port_type'):
            #     resource_type_set = o.output_port.output_port_type.resource_types
            #     pass

            workflowjob_runjob_map[wfjob_A] = runjob_A
            return runjob_A

        def runjob_creation_loop(this_ip_resource_map):
            """
            this_ip_resource_map - an OrderedDict containing (input_port, resource)
            pairs to guide the runjob creation process which input ports are taking
            an element from resource collection.
            """
            for wfjob in endpoint_workflowjobs:
                create_runjobs(wfjob, this_ip_resource_map)

            workflow_job_iteration = {}

            for wfjob in workflowjob_runjob_map:
                workflow_job_iteration[wfjob] = workflowjob_runjob_map[wfjob]

            for wfjob in workflow_job_iteration:
                if wfjob not in singleton_workflowjobs:
                    del workflowjob_runjob_map[wfjob]

        # Main:
        # Construct a list of list of (input_port, resource) pairs
        # The outer list corresponds to the total number of resource
        # collections assigned to the workflow execution. The inner
        # list corresponds to the length of every collection (validation
        # ensures they have same lengths)
        ip_resource_pairs_collection = []
        for ip, ress in resource_assignment_dict.items():
            if len(ress) > 1:
                ip_resource_pairs = list(map(lambda r: (ip, r), ress))
                ip_resource_pairs_collection.append(ip_resource_pairs)

        if ip_resource_pairs_collection:
            for ip_resource_pairs_each in zip(*ip_resource_pairs_collection):
                # We are iterating through a list of (input_port, resource) pairs
                # with all different input_port Convert it to a dictionary for
                # easier lookup. Use OrderedDict to make it easier to find the
                # first one in create_runjob_A.
                this_ip_resource_map = OrderedDict(ip_resource_pairs_each)
                runjob_creation_loop(this_ip_resource_map)
        else:
            runjob_creation_loop(OrderedDict({}))

        # ready to process
        workflow_run.status = task_status.PROCESSING
        workflow_run.save(update_fields=["status"])

        # call master_task
        registry.tasks["rodan.core.master_task"].apply_async((wfrun_id,))

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
            adjacent_connections = Connection.objects.filter(
                output_port__workflow_job=wfjob
            )
            for conn in adjacent_connections:
                adj_wfjob = WorkflowJob.objects.get(input_ports=conn.input_port)
                traversal(adj_wfjob)

        for wfjob in WorkflowJob.objects.filter(workflow=workflow):
            singleton_workflowjobs.append(wfjob)

        for ip, ress in resource_assignment_dict.items():
            if len(ress) > 1:
                initial_wfjob = ip.workflow_job
                traversal(initial_wfjob)

        return singleton_workflowjobs


"""
@task(name="rodan.core.process_workflowrun")
def process_workflowrun(wfrun_id):
    workflow_run = WorkflowRun.objects.get(uuid=wfrun_id)

    # ready to process
    workflow_run.status = task_status.PROCESSING
    workflow_run.save(update_fields=['status'])

    # call master_task
    registry.tasks['rodan.core.master_task'].apply_async((wfrun_id,))
"""


@task(name="rodan.core.cancel_workflowrun")
def cancel_workflowrun(wfrun_id):
    wfrun = WorkflowRun.objects.get(uuid=wfrun_id)
    runjobs_to_revoke_query = RunJob.objects.filter(
        workflow_run=wfrun,
        status__in=(
            task_status.SCHEDULED,
            task_status.PROCESSING,
            task_status.WAITING_FOR_INPUT,
        ),
    )
    runjobs_to_revoke_celery_id = runjobs_to_revoke_query.values_list(
        "celery_task_id", flat=True
    )
    for celery_id in runjobs_to_revoke_celery_id:
        if celery_id is not None:
            revoke(celery_id, terminate=True)
    runjobs_to_revoke_query.update(status=task_status.CANCELLED)
    wfrun.status = task_status.CANCELLED
    wfrun.save(update_fields=["status"])


@task(name="rodan.core.retry_workflowrun")
def retry_workflowrun(wfrun_id):
    wfrun = WorkflowRun.objects.get(uuid=wfrun_id)
    runjobs_to_retry_query = RunJob.objects.filter(
        workflow_run=wfrun, status__in=(task_status.FAILED, task_status.CANCELLED)
    )
    for rj in runjobs_to_retry_query:
        rj.status = task_status.SCHEDULED
        rj.error_summary = ""
        rj.error_details = ""
        original_settings = {}
        for k, v in rj.job_settings.items():
            if not k.startswith("@"):
                original_settings[k] = v
        rj.job_settings = original_settings
        rj.save(
            update_fields=["status", "job_settings", "error_summary", "error_details"]
        )

    wfrun.status = task_status.RETRYING
    wfrun.save(update_fields=["status"])
    registry.tasks["rodan.core.master_task"].apply_async((wfrun_id,))


@task(name="rodan.core.redo_runjob_tree")
def redo_runjob_tree(rj_id):
    """
    rj -- expected status should not be SCHEDULED.
    """
    rj = RunJob.objects.get(uuid=rj_id)
    wfrun = rj.workflow_run

    def inner_redo(rj):
        if rj.celery_task_id is not None:
            revoke(rj.celery_task_id, terminate=True)

        # 1. Revoke all downstream runjobs
        for o in rj.outputs.all():
            r = o.resource or o.resource_list
            for i in r.inputs.filter(
                Q(run_job__workflow_run=rj.workflow_run)
                & ~Q(run_job__status=task_status.SCHEDULED)
            ):
                inner_redo(i.run_job)

            # 2. Clear output resources
            if isinstance(r, Resource):
                rs = [r]
            else:
                rs = r.resources.all()

            for rr in rs:
                rr.has_thumb = False

        # 3. Reset status and clear interactive data
        original_settings = {}
        for k, v in rj.job_settings.items():
            if not k.startswith("@"):
                original_settings[k] = v
        rj.job_settings = original_settings
        rj.status = task_status.SCHEDULED
        rj.save(update_fields=["status", "job_settings"])

    inner_redo(rj)
    wfrun.status = task_status.RETRYING
    wfrun.save(update_fields=["status"])
    registry.tasks["rodan.core.master_task"].apply_async((wfrun.uuid.hex,))


@task(name="rodan.core.send_email")
def send_email(subject, body, to):
    email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, to)
    email.send()


@task(name="rodan.core.create_archive")
def create_archive(resource_uuids):
    """
    Creates a zip archive of resosurces in memory for a user to download
    """
    condition = Q()
    for uuid in resource_uuids:
        condition |= Q(uuid=uuid)
    resources = Resource.objects.filter(Q(resource_file__isnull=False) & condition)
    # Don't return an empty zip file
    if resources.count() == 0:
        return None
    temporary_storage = six.StringIO()
    with zipfile.ZipFile(temporary_storage, "a", zipfile.ZIP_DEFLATED) as archive:
        for resource in resources:
            if not resource.resource_file:
                print("{} has no file!".format(resource.name))
                continue

            # determine a path that doesn't conflict
            filepath = resource.name + "." + resource.resource_type.extension
            if filepath in archive.namelist():
                for i in six.moves.range(1, sys.maxint):
                    filepath = resource.name + " ({}).".format(i) + resource.resource_type.extension
                    if filepath not in archive.namelist():
                        break

            archive.write(
                resource.resource_file.path,
                filepath
            )

    temporary_storage.seek(0)
    return temporary_storage


class test_work(Task):
    name = "rodan.core.test_work"
    queue = "celery"

# app.tasks.register(create_resource())
# app.tasks.register(package_results())
# app.tasks.register(expire_package)
# app.tasks.register(create_workflowrun())
