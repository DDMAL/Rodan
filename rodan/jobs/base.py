import tempfile, shutil, os, uuid, copy, re, json, contextlib, jsonschema, inspect
from celery import Task, registry
from celery.app.task import TaskType
from rodan.models import RunJob, Input, Output, Resource, ResourceType, Job, InputPortType, OutputPortType, WorkflowRun
from rodan.constants import task_status
from django.conf import settings as rodan_settings
from django.core.files import File
from django.db.models import Prefetch
from django.template import Template
from rodan.exceptions import CustomAPIException
from rest_framework import status
from rodan.jobs.deep_eq import deep_eq
from rodan.jobs.convert_to_unicode import convert_to_unicode
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

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

        if not attrs['_abstract']:
            module_name = attrs['__module__']
            if module_name.startswith('rodan.jobs.'):
                attrs['_package_name'] = 'rodan.jobs.' + module_name[len('rodan.jobs.'):].split('.', 1)[0]
            else:
                if settings.TEST and module_name == "rodan.test.dummy_jobs":
                    attrs['_package_name'] = 'rodan.test.dummy_jobs'
                else:
                    raise ValueError('Invalid use of Rodan jobs - job package must locate in /rodan/jobs/')

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
            if not Job.objects.filter(name=attrs['name']).exists():
                if not getattr(settings, '_rodan_update_jobs', None) and not settings.TEST:
                    raise ImproperlyConfigured('You have to run `manage.py rodan_update_jobs` before starting Rodan server or any Rodan workers.')

                try:
                    # verify the schema
                    jsonschema.Draft4Validator.check_schema(attrs['settings'])
                except jsonschema.exceptions.SchemaError as e:
                    raise e
                schema = attrs['settings'] or {'type': 'object'}

                j = Job(name=attrs['name'],
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

                if not settings.TEST:
                    print "Added: {0}".format(j.name)
            else:
                UPDATE_JOBS = getattr(rodan_settings, "_rodan_update_jobs", False)
                # perform an integrity check, and update jobs if demanded.
                j = Job.objects.get(name=attrs['name'])

                def check_field(field_name, original_value, new_value, compare_fn=lambda x, y: x == y):
                    if not compare_fn(original_value, new_value):
                        if not UPDATE_JOBS:
                            raise ImproperlyConfigured("The field `{0}` of Job `{1}` seems to be updated: {2} --> {3}. Try to run `manage.py rodan_update_jobs` to confirm this update.".format(field_name, j.name, convert_to_unicode(original_value), convert_to_unicode(new_value)))
                        else:
                            confirm_update = raw_input("The field `{0}` of Job `{1}` seems to be updated: \n{2}\n  -->\n{3}\n\nConfirm (y/N)? ".format(field_name, j.name, convert_to_unicode(original_value), convert_to_unicode(new_value)))
                            if confirm_update.lower() == 'y':
                                setattr(j, field_name, new_value)
                                j.save()
                                print "  ..updated.\n\n"
                            else:
                                print "  ..not updated.\n\n"

                check_field("author", j.author, attrs['author'])
                check_field("description", j.description, attrs['description'])
                check_field("settings", j.settings, attrs['settings'] or {'type': 'object'}, compare_fn=lambda x, y: deep_eq(x, y))
                check_field("enabled", j.enabled, attrs['enabled'])
                check_field("category", j.category, attrs['category'])
                check_field("interactive", j.interactive, attrs['interactive'])


                # Input Port Types
                def check_port_types(which):
                    "which == 'in' or 'out'"
                    if which == 'in':
                        attrs_pts = list(copy.deepcopy(attrs['input_port_types']))
                        db_pts = list(j.input_port_types.all())
                        msg = 'Input'
                    elif which == 'out':
                        attrs_pts = list(copy.deepcopy(attrs['output_port_types']))
                        db_pts = list(j.output_port_types.all())
                        msg = 'Output'

                    for pt in db_pts:
                        pt_name = pt.name

                        idx = next((i for (i, this_pt) in enumerate(attrs_pts) if this_pt['name'] == pt_name), None)
                        if idx is not None:  # pt exists in database and in code. Check values
                            attrs_pt = attrs_pts[idx]

                            # Compare values
                            if attrs_pt['minimum'] != pt.minimum:
                                if not UPDATE_JOBS:
                                    raise ImproperlyConfigured("The field `{0}` of {5} Port Type `{1}` of Job `{2}` seems to be updated: {3} --> {4}. Try to run `manage.py rodan_update_jobs` to confirm this update.".format('minimum', pt_name, j.name, pt.minimum, attrs_pt['minimum'], msg))
                                else:
                                    confirm_update = raw_input("The field `{0}` of {5} Port Type `{1}` of Job `{2}` seems to be updated: \n{3}\n  -->\n{4}\n\nConfirm (y/N)? ".format('minimum', pt_name, j.name, pt.minimum, attrs_pt['minimum'], msg))
                                    if confirm_update.lower() == 'y':
                                        pt.minimum = attrs_pt['minimum']
                                        pt.save()
                                        print "  ..updated.\n\n"
                                    else:
                                        print "  ..not updated.\n\n"

                            if attrs_pt['maximum'] != pt.maximum:
                                if not UPDATE_JOBS:
                                    raise ImproperlyConfigured("The field `{0}` of {5} Port Type `{1}` of Job `{2}` seems to be updated: {3} --> {4}. Try to run `manage.py rodan_update_jobs` to confirm this update.".format('maximum', pt_name, j.name, pt.maximum, attrs_pt['maximum'], msg))
                                else:
                                    confirm_update = raw_input("The field `{0}` of {5} Port Type `{1}` of Job `{2}` seems to be updated: \n{3}\n  -->\n{4}\n\nConfirm (y/N)? ".format('maximum', pt_name, j.name, pt.maximum, attrs_pt['maximum'], msg))
                                    if confirm_update.lower() == 'y':
                                        pt.maximum = attrs_pt['maximum']
                                        pt.save()
                                        print "  ..updated.\n\n"
                                    else:
                                        print "  ..not updated.\n\n"


                            resource_types = RodanTaskType._resolve_resource_types(attrs_pt['resource_types'])
                            rt_code = set(map(lambda rt: rt.mimetype, resource_types))
                            rt_db = set(map(lambda rt: rt.mimetype, pt.resource_types.all()))
                            if rt_code != rt_db:
                                if not UPDATE_JOBS:
                                    raise ImproperlyConfigured("The field `{0}` of {5} Port Type `{1}` of Job `{2}` seems to be updated: {3} --> {4}. Try to run `manage.py rodan_update_jobs` to confirm this update.".format('resource_types', pt_name, j.name, rt_db, rt_code, msg))
                                else:
                                    confirm_update = raw_input("The field `{0}` of {5} Port Type `{1}` of Job `{2}` seems to be updated: \n{3}\n  -->\n{4}\n\nConfirm (y/N)? ".format('resource_types', pt_name, j.name, rt_db, rt_code, msg))
                                    if confirm_update.lower() == 'y':
                                        pt.resource_types.clear()
                                        pt.resource_types.add(*resource_types)
                                        print "  ..updated.\n\n"
                                    else:
                                        print "  ..not updated.\n\n"

                            del attrs_pts[idx]

                        else:  # pt exists in database but not in code. Should be deleted.
                            if not UPDATE_JOBS:
                                raise ImproperlyConfigured("The {2} Port Type `{0}` of Job `{1}` seems to be deleted. Try to run `manage.py rodan_update_jobs` to confirm this deletion.".format(pt_name, j.name, msg))
                            else:
                                confirm_delete = raw_input("The {2} Port Type `{0}` of Job `{1}` seems to be deleted. Confirm (y/N)? ".format(pt_name, j.name, msg))
                                if confirm_delete.lower() == 'y':
                                    try:
                                        pt.delete()
                                        print "  ..deleted.\n\n"
                                    except Exception as e:
                                        print "  ..not deleted because of an exception: {0}. Please fix it manually.\n\n".format(str(e))
                                else:
                                    print "  ..not deleted.\n\n"

                    if attrs_pts:  # ipt exists in code but not in database. Should be added to the database.
                        for pt in attrs_pts:
                            if not UPDATE_JOBS:
                                raise ImproperlyConfigured("The {2} Port Type `{0}` of Job `{1}` seems to be newly added. Try to run `manage.py rodan_update_jobs` to confirm this update.".format(pt['name'], j.name, msg))
                            else:
                                confirm_update = raw_input("The {2} Port Type `{0}` of Job `{1}` seems to be newly added. Confirm (y/N)? ".format(pt['name'], j.name, msg))
                                if confirm_update.lower() == 'y':
                                    if which == 'in':
                                        Model = InputPortType
                                    elif which == 'out':
                                        Model = OutputPortType
                                    i = Model(job=j,
                                              name=pt['name'],
                                              minimum=pt['minimum'],
                                              maximum=pt['maximum'])
                                    i.save()
                                    resource_types = RodanTaskType._resolve_resource_types(pt['resource_types'])
                                    if len(resource_types) == 0:
                                        raise ValueError('No available resource types found for this {1}PortType: {0}'.format(pt['resource_types'], msg))
                                    i.resource_types.add(*resource_types)
                                    print "  ..updated.\n\n"
                                else:
                                    print "  ..not updated.\n\n"

                check_port_types('in')
                check_port_types('out')

            # Process done
            from rodan.jobs.load import job_list
            if attrs['name'] in job_list:
                job_list.remove(attrs['name'])

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
            d = {'resource_path': str(input_value['resource__compat_resource_file']),   # convert 'unicode' object to 'str' object for consistency
                 'resource_type': input_value['resource__resource_type__mimetype']}

            if with_urls:
                r = Resource.objects.get(uuid=input_value['resource__uuid'])
                d['resource_url'] = r.compat_file_url
                d['small_thumb_url'] = r.small_thumb_url
                d['medium_thumb_url'] = r.medium_thumb_url
                d['large_thumb_url'] = r.large_thumb_url
                d['diva_object_data'] = r.diva_json_url
                d['diva_iip_server'] = getattr(rodan_settings, 'IIPSRV_URL')
                d['diva_image_dir'] = r.diva_image_dir

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
        j_settings = Job.objects.get(name=runjob.job_name).settings

        for properti, definition in j_settings.get('properties', {}).iteritems():
            if 'enum' in definition:  # convert enum to integers
                rj_settings[properti] = definition['enum'].index(rj_settings[properti])

        return rj_settings

    def _package_path(self):
        base_path = os.path.dirname(settings.PROJECT_PATH)
        rel_path = os.sep.join(self._package_name.split('.'))
        return os.path.join(base_path, rel_path)  # e.g.: "/path/to/rodan/jobs/gamera"

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
        print 'WARNING: {0}.test_my_task() is not implemented.'.format(type(self).__module__)

    #######################
    # Utilities
    #######################
    class WAITING_FOR_INPUT(object):
        """
        As a possible return value of run_my_task() to indicate the interactive phase
        of the job, and return value of validate_my_user_input() to indicate the job
        staying in interactive phase.

        It holds the settings that need to be updated. The name of the settings must
        start with "@" in order to be distinguished from original settings. Keys not
        starting with "@" will be removed. Example:

            return self.WAITING_FOR_INPUT({'@field1': newVal1, '@field2': newVal2})

        The `response` attribute is for the manual phase returning HTTP responses.
        """
        def __init__(self, settings_update={}, response=None):
            self.settings_update = {}
            self.response = response
            for k, v in settings_update.iteritems():
                if isinstance(k, basestring) and k.startswith('@'):
                    self.settings_update[k] = v

    def tempdir(self):
        """
        A shortcut for all jobs.

        Usage:
            with self.tempdir() as tempdir:
        """
        return TemporaryDirectory()

    #############################################
    # Automatic phase -- running in Celery thread
    #############################################
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

        with self.tempdir() as tmpdir:
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
                runjob.celery_task_id = None
                runjob.save(update_fields=['status', 'job_settings', 'error_summary', 'error_details', 'celery_task_id'])
                return 'WAITING FOR INPUT'
            else:
                # ensure the job has produced all output files
                for opt_name, output_list in outputs.iteritems():
                    for output in output_list:
                        if not os.path.isfile(output['resource_temp_path']):
                            raise RuntimeError("The job did not produce the output file for {0}".format(opt_name))

                # save outputs
                for temppath, output in temppath_map.iteritems():
                    with open(temppath, 'rb') as f:
                        resource = Output.objects.get(uuid=output['uuid']).resource
                        resource.compat_resource_file.save(temppath, File(f), save=False) # Django will resolve the path according to upload_to
                        resource.save(update_fields=['compat_resource_file'])

                        registry.tasks['rodan.core.create_thumbnails'].run(resource.uuid.hex) # call synchronously
                        registry.tasks['rodan.core.create_diva'].run(resource.uuid.hex) # call synchronously

                runjob.status = task_status.FINISHED
                runjob.error_summary = None
                runjob.error_details = None
                runjob.celery_task_id = None
                runjob.save(update_fields=['status', 'error_summary', 'error_details', 'celery_task_id'])

                # Call master task.
                master_task = registry.tasks['rodan.core.master_task']
                wfrun_id = str(runjob.workflow_run.uuid)
                mt_retval = master_task.run(wfrun_id)
                return "FINISHED  |  master_task: {0}".format(mt_retval)

    def run_my_task(self, inputs, settings, outputs):
        raise NotImplementedError()

    def my_error_information(self, exc, traceback):
        raise NotImplementedError()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        runjob_id = args[0]

        update = self._add_error_information_to_runjob(exc, einfo)
        update['status'] = task_status.FAILED
        update['celery_task_id'] = None
        RunJob.objects.filter(pk=runjob_id).update(**update)
        wfrun_id = RunJob.objects.filter(pk=runjob_id).values_list('workflow_run__uuid', flat=True)[0]
        WorkflowRun.objects.filter(uuid=wfrun_id).update(status=task_status.FAILED)

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
        global _django_template_cache

        runjob = RunJob.objects.get(uuid=runjob_id)
        inputs = self._inputs(runjob, with_urls=True)
        settings = self._settings(runjob)

        partial_template_file, context = self.get_my_interface(inputs, settings)

        if isinstance(partial_template_file, Template):   # only in dummy_manual_job!
            return (partial_template_file, context)

        template_file = os.path.join(self._package_path(), partial_template_file)

        if template_file in _django_template_cache:
            return (_django_template_cache[template_file], context)
        else:
            with open(template_file, 'r') as f:
                t = Template(f.read())
                _django_template_cache = t
                return (t, context)


    def get_my_interface(self, inputs, settings):
        """
        inputs will contain:
        resource_path, resource_type, resource_url, small_thumb_url, medium_thumb_url,
        large_thumb_url

        Should return: (template, context), template is the relative path (relative to
        the path of package folder) to the interface HTML template file (in Django
        template language), and context should be a dictionary.

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


_django_template_cache = {}
