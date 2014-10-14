import tempfile, shutil, os, uuid, copy
from celery import Task
from rodan.models.runjob import RunJobStatus
from rodan.models import RunJob, Input, Output, Resource
from rodan.jobs.util import taskutil
from rodan.helpers.thumbnails import create_thumbnails
from rodan.helpers.processed import processed
from django.conf import settings as rodan_settings
from django.core.files import File
from rodan.models.resource import ResourceType


class RodanTask(Task):
    # code here are run asynchronously. Any write to database should use `queryset.update()` method, instead of `obj.save()`.
    # Specific jobs that inherit the base class should not touch database.

    def run(self, runjob_id):
        settings = RunJob.objects.filter(uuid=runjob_id).values_list('job_settings', flat=True)[0]
        inputs = self._inputs(runjob_id)
        temp_dir = tempfile.mkdtemp()
        outputs = self._outputs(runjob_id, temp_dir)

        # build argument for run_my_task and mapping dictionary
        arg_outputs = {}
        temppath_map = {}
        for opt_name, output_list in outputs.iteritems():
            if opt_name not in arg_outputs:
                arg_outputs[opt_name] = []
            for output in output_list:
                arg_outputs[opt_name].append({
                    'resource_path': output['resource_temp_path'],
                    'resource_type': output['resource_type']
                })
                temppath_map[output['resource_temp_path']] = output
        retval = self.run_my_task(inputs, settings, arg_outputs)

        # save outputs
        for temppath, output in temppath_map.iteritems():
            with open(temppath, 'rb') as f:
                o = Output.objects.get(uuid=output['uuid'])
                o.resource.compat_resource_file.save(temppath, File(f), save=False) # Django will resolve the path according to upload_to
                path = o.resource.compat_resource_file.path
                res_query = Resource.objects.filter(outputs__uuid=output['uuid'])
                res_query.update(compat_resource_file=path)

        shutil.rmtree(temp_dir)
        return retval

    def run_my_task(self, inputs, settings, outputs):
        raise NotImplementedError()

    def error_information(self, exc, traceback):
        raise NotImplementedError()


    def on_success(self, retval, task_id, args, kwargs):
        RunJob.objects.filter(pk=args[0]).update(status=RunJobStatus.HAS_FINISHED,
                                                 error_summary='',
                                                 error_details='')
        #### [TODO] modify these helpers, and execute them only when the output are image type
        #res = create_thumbnails.s(result)
        #res.link(processed.s())
        #res.apply_async()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        runjob_id = args[0]

        update = self._add_error_information_to_runjob(exc, einfo)
        update['status'] = RunJobStatus.FAILED
        RunJob.objects.filter(pk=runjob_id).update(**update)

    def _add_error_information_to_runjob(self, exc, einfo):
        # Any job using the default_on_failure method can define an error_information
        # method, which will take in an exception and a traceback string,
        # and return a dictionary containing 'error_summary' and 'error_details'.
        # This is to allow pretty formatting of error messages in the client.
        # If any StandardError is raised in the process of retrieving the
        # values, the default values are used for both fields.
        try:
            err_info = self.error_information(exc, einfo.traceback)
            err_summary = err_info['error_summary']
            err_details = err_info['error_details']
            if rodan_settings.TRACEBACK_IN_ERROR_DETAIL:
                err_details = str(err_details) + "\n\n" + str(einfo.traceback)
        except Exception as e:
            print "The error_information method is not implemented properly (or not implemented at all). Exception: "
            print "%s: %s" % (e.__class__.__name__, e.__str__())
            print "Using default sources for error information."
            err_summary = exc.__class__.__name__
            err_details = einfo.traceback

        return {'error_summary': err_summary,
                'error_details': err_details}

    def _inputs(self, runjob_id):
        "Return a dictionary of list of input file path and input resource type."
        input_values = Input.objects.filter(run_job__pk=runjob_id).values(
            'input_port__input_port_type__name',
            'resource__compat_resource_file',
            'resource__resource_type')

        inputs = {}
        for input_value in input_values:
            ipt_name = input_value['input_port__input_port_type__name']
            if ipt_name not in inputs:
                inputs[ipt_name] = []
            inputs[ipt_name].append({'resource_path': input_value['resource__compat_resource_file'],
                                     'resource_type': input_value['resource__resource_type']})
        return inputs

    def _outputs(self, runjob_id, temp_dir):
        "Return a dictionary of list of output file path and output resource type."
        output_values = Output.objects.filter(run_job__pk=runjob_id).values(
            'output_port__output_port_type__name',
            'resource__resource_type',
            'uuid')

        outputs = {}
        for output_value in output_values:
            opt_name = output_value['output_port__output_port_type__name']
            if opt_name not in outputs:
                outputs[opt_name] = []

            output_res_type = output_value['resource__resource_type']
            output_res_ext = ResourceType.get_extension(output_res_type)
            if output_res_ext is None:
                output_res_tempname = "{0}".format(str(uuid.uuid4()))
            else:
                output_res_tempname = "{0}.{1}".format(str(uuid.uuid4()), output_res_ext)
            output_res_temppath = os.path.join(temp_dir, output_res_tempname)

            outputs[opt_name].append({'resource_type': output_res_type,
                                      'resource_temp_path': output_res_temppath,
                                      'uuid': output_value['uuid']})
        return outputs
