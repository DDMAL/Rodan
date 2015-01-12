import tempfile, shutil, os, uuid, copy, re, json, contextlib, jsonschema, inspect
from celery import Task, registry
from celery.app.task import TaskType
from rodan.models import RunJob, Input, Output, Resource, ResourceType, Job, InputPortType, OutputPortType, WorkflowRun
from rodan.constants import task_status
from django.conf import settings as rodan_settings
from django.core.files import File
from django.db.models import Prefetch
from rodan.exceptions import CustomAPIException
from rest_framework import status

import logging
logger = logging.getLogger('rodan')

class RodanTaskType(TaskType):
    """
    This is the metaclass for RodanTask base class.

    Every time a new task inherits RodanTask, __init__ method of this metaclass is
    triggered, which registers the new task in Rodan database.

    Note: TaskType is the metaclass of Task (Celery objects)
    """
    def __new__(cls, clsname, bases, attrs):
        attrs['_abstract'] = attrs.get('abstract')  # Keep a copy as Celery TaskType will delete it.
        return TaskType.__new__(cls, clsname, bases, attrs)

    def __init__(cls, clsname, bases, attrs):
        super(RodanTaskType, cls).__init__(clsname, bases, attrs)

        # check the number of arguments of implemented function
        if 'run_my_task' in attrs:
            argspec = inspect.getargspec(attrs['run_my_task'])
            assert len(argspec.args) == 4, 'run_my_task'
        if 'get_my_interface' in attrs:
            argspec = inspect.getargspec(attrs['get_my_interface'])
            assert len(argspec.args) == 3, 'get_my_interface'
        if 'validate_my_user_input' in attrs:
            argspec = inspect.getargspec(attrs['validate_my_user_input'])
            assert len(argspec.args) == 4, 'validate_my_user_input'
        if 'test_my_task' in attrs:
            argspec = inspect.getargspec(attrs['test_my_task'])
            assert len(argspec.args) == 2, 'test_my_task'

        if attrs.get('_abstract') == True:  # not the abstract class
            return
        else:
            if not Job.objects.filter(job_name=attrs['name']).exists():
                try:
                    # verify the schema
                    jsonschema.Draft4Validator.check_schema(attrs['settings'])
                except jsonschema.exceptions.SchemaError as e:
                    raise e
                schema = attrs['settings'] or {'type': 'object'}

                j = Job(job_name=attrs['name'],
                        author=attrs['author'],
                        description=attrs['description'],
                        settings=schema,
                        enabled=attrs['enabled'],
                        category=attrs['category'],
                        interactive=attrs['interactive'])
                j.save()

                try:
                    for ipt in attrs['input_port_types']:
                        i = InputPortType(job=j,
                                          name=ipt['name'],
                                          minimum=ipt['minimum'],
                                          maximum=ipt['maximum'])
                        i.save()
                        resource_types = RodanTaskType._resolve_resource_types(ipt['resource_types'])
                        if len(resource_types) == 0:
                            raise ValueError('No available resource types found for this InputPortType: {0}'.format(ipt['resource_types']))
                        i.resource_types.add(*resource_types)

                    for opt in attrs['output_port_types']:
                        o = OutputPortType(job=j,
                                           name=opt['name'],
                                           minimum=opt['minimum'],
                                           maximum=opt['maximum'])
                        o.save()
                        resource_types = RodanTaskType._resolve_resource_types(opt['resource_types'])
                        if len(resource_types) == 0:
                            raise ValueError('No available resource types found for this OutputPortType: {0}'.format(opt['resource_types']))
                        o.resource_types.add(*resource_types)
                except Exception as e:
                    j.delete()  # clean the job
                    raise e
            else:
                # perform an integrity check
                j = Job.objects.get(job_name=attrs['name'])
                errmsg = "Integrity error: Job {0}. Delete this job in Django shell and restart Rodan?".format(attrs['name'])
                assert j.author == attrs['author'], errmsg
                assert j.description == attrs['description'], errmsg
                #assert set(j.settings) == set(attrs['settings']), errmsg
                assert j.enabled == attrs['enabled'], errmsg
                assert j.category == attrs['category'], errmsg
                assert j.interactive == attrs['interactive'], errmsg

                assert len(attrs['input_port_types']) == j.input_port_types.count(), errmsg
                for ipt in j.input_port_types.all():
                    ipt_name = ipt.name
                    i = filter(lambda d: d['name'] == ipt_name, attrs['input_port_types'])
                    assert len(i) == 1, errmsg
                    i = i[0]
                    assert i['minimum'] == ipt.minimum, errmsg
                    assert i['maximum'] == ipt.maximum, errmsg
                    resource_types = RodanTaskType._resolve_resource_types(i['resource_types'])
                    assert set(map(lambda rt: rt.mimetype, resource_types)) == set(map(lambda rt: rt.mimetype, ipt.resource_types.all())), errmsg

                assert len(attrs['output_port_types']) == j.output_port_types.count(), errmsg
                for opt in j.output_port_types.all():
                    opt_name = opt.name
                    o = filter(lambda d: d['name'] == opt_name, attrs['output_port_types'])
                    assert len(o) == 1, errmsg
                    o = o[0]
                    assert o['minimum'] == opt.minimum, errmsg
                    assert o['maximum'] == opt.maximum, errmsg
                    resource_types = RodanTaskType._resolve_resource_types(o['resource_types'])
                    assert set(map(lambda rt: rt.mimetype, resource_types)) == set(map(lambda rt: rt.mimetype, opt.resource_types.all())), errmsg

    @staticmethod
    def _resolve_resource_types(value):
        """
        `value` should be one of:
        - a list of strings of mimetypes
        - a callable which receives one parameter (as a filter)

        Returns a list of ResourceType objects.
        """
        try:
            mimelist = filter(value, ResourceType.all_mimetypes())
        except TypeError:
            mimelist = value
        return ResourceType.cached_list(mimelist)


class RodanTask(Task):
    __metaclass__ = RodanTaskType
    abstract = True

    ################################
    # Private retrieval methods
    ################################
    def _inputs(self, runjob, with_urls=False):
        """
        Return a dictionary of list of input file path and input resource type.
        If with_urls=True, it also includes the compat resource url and thumbnail urls.
        """
        values = ['input_port_type_name',
                  'resource__compat_resource_file',
                  'resource__resource_type__mimetype']
        if with_urls:
            values.append('resource__uuid')
        input_values = Input.objects.filter(run_job=runjob).values(*values)

        inputs = {}
        for input_value in input_values:
            ipt_name = input_value['input_port_type_name']
            if ipt_name not in inputs:
                inputs[ipt_name] = []
            d = {'resource_path': input_value['resource__compat_resource_file'],
                 'resource_type': input_value['resource__resource_type__mimetype']}

            if with_urls:
                r = Resource.objects.get(uuid=input_value['resource__uuid'])
                d['resource_url'] = r.compat_file_url
                d['small_thumb_url'] = r.small_thumb_url
                d['medium_thumb_url'] = r.medium_thumb_url
                d['large_thumb_url'] = r.large_thumb_url

            inputs[ipt_name].append(d)
        return inputs

    def _outputs(self, runjob, temp_dir):
        "Return a dictionary of list of output file path and output resource type."
        output_values = Output.objects.filter(run_job=runjob).values(
            'output_port_type_name',
            'resource__resource_type__mimetype',
            'uuid')

        outputs = {}
        for output_value in output_values:
            opt_name = output_value['output_port_type_name']
            if opt_name not in outputs:
                outputs[opt_name] = []

            output_res_tempname = str(uuid.uuid4())
            output_res_temppath = os.path.join(temp_dir, output_res_tempname)

            outputs[opt_name].append({'resource_type': output_value['resource__resource_type__mimetype'],
                                      'resource_temp_path': output_res_temppath,
                                      'uuid': output_value['uuid']})
        return outputs

    def _settings(self, runjob):
        rj_settings = runjob.job_settings
        j_settings = Job.objects.get(job_name=runjob.job_name).settings

        for properti, definition in j_settings.get('properties', {}).iteritems():
            if 'enum' in definition:  # convert enum to integers
                rj_settings[properti] = definition['enum'].index(rj_settings[properti])

        return rj_settings

    ########################
    # Test interface
    ########################
    def test_my_task(self, testcase):
        """
        This method is called when executing `manage.py test test_all_jobs`.

        This method should call `run_my_task()` and/or `get_my_interface()` and/or
        `validate_my_user_input`. Before calling the job code, this method needs to
        construct `inputs`, `settings`, and `outputs` objects as parameters of the
        job code.

        Its own parameter `testcase` refers to the Python TestCase object. Aside from
        assertion methods like `assertEqual()` and `assertRaises()`, it provides
        `new_available_path()` which returns a path to a nonexist file. `test_my_task`
        method can thus create an input file and pass into the job code.
        """
        raise NotImplementedError('{0}.test_my_task() is not implemented.'.format(type(self).__module__))

    #############################################
    # Automatic phase -- running in Celery thread
    #############################################
    class WAITING_FOR_INPUT(object):
        """
        As a possible return value of run_my_task() to indicate the interactive phase
        of the job.

        It holds the settings that need to be updated. The name of the settings must
        start with "@" in order to be distinguished from original settings. Keys not
        starting with "@" will be removed. Example:

            return self.WAITING_FOR_INPUT({'@field1': newVal1, '@field2': newVal2})
        """
        def __init__(self, settings_update={}):
            self.settings_update = {}
            for k, v in settings_update.iteritems():
                if isinstance(k, basestring) and k.startswith('@'):
                    self.settings_update[k] = v

    def run(self, runjob_id):
        """
        Code here are run asynchronously in Celery thread.

        To prevent re-creating a deleted object, any write to database should use
        one of the following:
        + `queryset.update()`
        + `obj.save(update_fields=[...])`
        + `obj.file_field.save(..., save=False)` + `obj.save(update_fields=['file_field'])`

        instead of:
        + `obj.save()`
        + `obj.file_field.save(..., save=True)`
        """
        runjob = RunJob.objects.get(uuid=runjob_id)
        settings = self._settings(runjob)
        inputs = self._inputs(runjob)

        with TemporaryDirectory() as tmpdir:
            outputs = self._outputs(runjob, tmpdir)

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

            if isinstance(retval, self.WAITING_FOR_INPUT):
                settings.update(retval.settings_update)

                runjob.status = task_status.WAITING_FOR_INPUT
                runjob.job_settings = settings
                runjob.error_summary = None
                runjob.error_details = None
                runjob.save(update_fields=['status', 'job_settings', 'error_summary', 'error_details'])
            else:
                # save outputs
                for temppath, output in temppath_map.iteritems():
                    with open(temppath, 'rb') as f:
                        resource = Output.objects.get(uuid=output['uuid']).resource
                        resource.compat_resource_file.save(temppath, File(f), save=False) # Django will resolve the path according to upload_to
                        resource.save(update_fields=['compat_resource_file'])

                        registry.tasks['rodan.core.create_thumbnails'].run(resource.uuid.hex) # call synchronously

                runjob.status = task_status.FINISHED
                runjob.error_summary = None
                runjob.error_details = None
                runjob.save(update_fields=['status', 'error_summary', 'error_details'])

    def run_my_task(self, inputs, settings, outputs):
        raise NotImplementedError()

    def my_error_information(self, exc, traceback):
        raise NotImplementedError()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        runjob_id = args[0]

        update = self._add_error_information_to_runjob(exc, einfo)
        update['status'] = task_status.FAILED
        RunJob.objects.filter(pk=runjob_id).update(**update)
        wfrun_id = RunJob.objects.filter(pk=runjob_id).values_list('workflow_run__uuid', flat=True)[0]
        WorkflowRun.objects.filter(uuid=wfrun_id).update(status=task_status.FAILED)
        RunJob.objects.filter(workflow_run=wfrun_id, status=task_status.SCHEDULED).update(status=task_status.CANCELLED)

    def _add_error_information_to_runjob(self, exc, einfo):
        # Any job using the default_on_failure method can define an error_information
        # method, which will take in an exception and a traceback string,
        # and return a dictionary containing 'error_summary' and 'error_details'.
        # This is to allow pretty formatting of error messages in the client.
        # If any StandardError is raised in the process of retrieving the
        # values, the default values are used for both fields.
        try:
            err_info = self.my_error_information(exc, einfo.traceback)
            err_summary = err_info['error_summary']
            err_details = err_info['error_details']
            if rodan_settings.TRACEBACK_IN_ERROR_DETAIL:
                err_details = str(err_details) + "\n\n" + str(einfo.traceback)
        except Exception as e:
            logger.warning("The my_error_information method is not implemented properly (or not implemented at all). Exception: ")
            logger.warning("%s: %s" % (e.__class__.__name__, e.__str__()))
            logger.warning("Using default sources for error information.")
            err_summary = "{0}: {1}".format(type(exc).__name__, str(exc))
            err_details = einfo.traceback

        return {'error_summary': err_summary,
                'error_details': err_details}

    ##########################################
    # Manual phase -- running in Django thread
    ##########################################
    def get_interface(self, runjob_id):
        runjob = RunJob.objects.get(uuid=runjob_id)
        inputs = self._inputs(runjob, with_urls=True)
        settings = self._settings(runjob)
        return self.get_my_interface(inputs, settings)

    def get_my_interface(self, inputs, settings):
        """
        inputs will contain:
        resource_path, resource_type, resource_url, small_thumb_url, medium_thumb_url,
        large_thumb_url

        Should return: (template, context), template is a Django Template object,
        and context should be a dictionary.

        could raise self.ManualPhaseException
        """
        raise NotImplementedError()

    def validate_user_input(self, runjob_id, user_input):
        runjob = RunJob.objects.get(uuid=runjob_id)
        inputs = self._inputs(runjob)
        settings = self._settings(runjob)

        try:
            return self.validate_my_user_input(inputs, settings, user_input)
        except self.ManualPhaseException:
            raise

    def validate_my_user_input(self, inputs, settings, user_input):
        """
        inputs will contain:
        resource_path, resource_type

        could raise rodan.jobs.base.ManualJobException

        should return a dictionary of the update of settings. The keys should start with
        '@' or they will be discarded.
        """
        raise NotImplementedError()

    class ManualPhaseException(CustomAPIException):
        def __init__(self, errmsg):
            super(RodanTask.ManualPhaseException, self).__init__(errmsg, status=status.HTTP_400_BAD_REQUEST)



@contextlib.contextmanager
def TemporaryDirectory():
    """
    Temporary directory with automatic cleanup.
    see -- http://stackoverflow.com/questions/13379742/right-way-to-clean-up-a-temporary-folder-in-python-class
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)
