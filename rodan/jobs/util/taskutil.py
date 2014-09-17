import os
import re
import shutil
import tempfile
import uuid
import urlparse
import functools
from django.conf import settings as rodan_settings
from django.core.files import File
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.jobs.gamera import argconvert
from rodan.helpers.thumbnails import create_thumbnails
from rodan.helpers.exceptions import InvalidFirstJobError, UUIDParseError, ObjectDeletedError
from rodan.helpers.processed import processed
from rodan.helpers.dbmanagement import exists_in_db, refetch_from_db, resolve_object_from_url

IMAGE_TYPES = rodan_settings.IMAGE_TYPES

def execute_unless_deleted(db_object, partial_func):
    if db_object.pk:
        if exists_in_db(db_object):
            partial_func()
        else:
            raise ObjectDeletedError("The object {0} has been deleted from the database. Aborting save.".format(db_object))
    else:
        # If the object doesn't have a primary key we assume that it being newly created and this safe to touch the database.
        partial_func()


def save_instance(db_object):
    """
    In asynchronous tasks, always use this method instead of the default django save method.
    This saves an object only if it was not deleted from the database.
    """
    execute_unless_deleted(db_object, functools.partial(db_object.save))


def save_file_field(file_field_object, *args, **kwargs):
    """
    Saving a file object in a django FileField saves the model instance by default.
    In asynchronous tasks, we want to make sure we don't resave a deleted database record.
    This function abstracts away that database check.

    Arguments:
        file_field_object: The FileField object of the instance that you're trying to save.
        *args, **kwargs: All the arguments and keyword arguments that you would
                         usually pass into the FileField.save() method.
     """
    if 'save' in kwargs and kwargs['save'] == False:
        file_field_object.save(*args, **kwargs)

    else:
        execute_unless_deleted(file_field_object.instance,
                               functools.partial(file_field_object.save, *args, **kwargs))


def set_runjob_status(runjob, status):
    runjob.status = status
    save_instance(runjob)
    return refetch_from_db(runjob)

def set_running(runjob):
    set_runjob_status(runjob, RunJobStatus.RUNNING)


def set_run_once_waiting(runjob):
    set_runjob_status(runjob, RunJobStatus.RUN_ONCE_WAITING)


def init_result(runjob):
    new_result = Result(run_job=runjob)
    new_result.save()
    return new_result


def get_page_url(runjob, result_id):
    if result_id is None:
        # this is the first job in a run
        page = runjob.page.compat_file_path
    else:
        # we take the page image we want to operate on from the previous result object
        result = Result.objects.get(pk=result_id)
        page = result.result.path

    return page


def get_input_path(runjob, result_id):
    runjob_input_types = runjob.workflow_job.job.input_types['pixel_types']
    if all(runjob_input_types) in IMAGE_TYPES:
        return get_page_url(runjob, result_id)
    elif result_id is None:
        raise InvalidFirstJobError("This cannot be the first job. This job takes a non-image type as input.")
    else:
        result = Result.objects.get(pk=result_id)
        return result.result.path


def get_uuid_from_url(url):
    """
    This function returns the last UUID present in a url. The UUID
    must be at the end of the url. The trailing slash is optinal.
    Query parameters are considered to be not part of the url.
    The UUID should be 32 adjacent characters, unhyphenated.
    Only http/https scheme is supported. It also works if no scheme is
    provided, so relative urls are okay.

    Example: All of the following will return
    12345678901234567890123456abcdef as the UUID:

    http://idontcare.org/12345678901234567890123456abcdef
    http://idontcare.org/12345678901234567890123456abcdef/
    http://idontcare.org/1abc2319bc11234567890123deadbeef/blah/blah/12345678901234567890123456abcdef
    http://idontcare.org/12345678901234567890123456abcdef/?cooloption=true
    relpath/12345678901234567890123456abcdef?cooloption=true
    12345678901234567890123456abcdef


    The following will raise exceptions:

    http://idontcare.org/12345678901234567890123456abcde
    http://idontcare.org/12345678901234567890123456abcdeff
    http://idontcare.org/12345678-9012-3456-7890-123456abcdef
    12345678-9012-3456-7890-123456abcdef

    """

    url = str(url)
    url = urlparse.urlparse(url).path
    print "Trying to extract uuid from " + url
    re_uuid = re.compile(r'^(.*)/(?P<uuid>[0-9a-f]{32})/?$', re.IGNORECASE)
    match_object = re_uuid.match(url)

    if match_object:
        return match_object.group('uuid')

    # Last try to see if a real uuid was passed in instead of an url.
    re_no_url_uuid = re.compile(r'^(?P<uuid>[0-9a-f]{32})$', re.IGNORECASE)
    match_object = re_no_url_uuid.match(url)

    if match_object:
        return match_object.group('uuid')

    raise UUIDParseError("Unable to extract UUID from {0}".format(url))


def get_settings(runjob):
    # Note that the runtime value is passed inside the 'default' field.
    settings = {}
    for s in runjob.job_settings:
        setting_name = "_".join(s['name'].split(" "))
        setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
        settings[setting_name] = setting_value

    return settings


def apply_updates(runjob, updates):
    while updates:
        setting_name, value = updates.popitem()
        for setting in runjob.job_settings:
            if setting['name'] == setting_name:
                setting['default'] = value
    save_instance(runjob)


def create_temp_path(ext=None):
    tdir = tempfile.mkdtemp()
    if ext is None:
        result_file = "{0}".format(str(uuid.uuid4()))
        return os.path.join(tdir, result_file)
    else:
        result_file = "{0}.{1}".format(str(uuid.uuid4()), ext)
        return os.path.join(tdir, result_file)


def save_result(result, result_temp_path):
    # Copy over temp file to appropriate result path, and delete temps.
    # Since the temps are deleted, this method is not indempotent.
    # Best used as a helper method.
    tdir, result_file = os.path.split(result_temp_path)
    result_save_path = result.result_path
    f = open(result_temp_path)
    save_file_field(result.result, os.path.join(result_save_path, result_file), File(f))
    f.close()
    shutil.rmtree(tdir)


def save_result_as_png(result_image, runjob):
    temp_path = create_temp_path(ext="png")
    try:
        result_image.save_image(temp_path)
    except AttributeError as e:
        # Debugging
        print "The process_image method probably did not return a valid gamera image."
        print "Did you forget to override process_image or add a return statement?"
        print "Error:"
        print e
    else:
        result = init_result(runjob)
        save_result(result, temp_path)
        return result


def if_runjob_not_cancelled(method_type):
    """
    You can use this decorator to make any 'run', 'on_success' or 'on_failure'
    method support runjob cancellation.
    """
    if method_type in ['on_success', 'on_failure']:
        def wrap(f):
            @functools.wraps(f)
            def wrapped_f(*args, **kwargs):
                inner_args = args[3]
                runjob_id = inner_args[1]
                runjob = RunJob.objects.get(pk=runjob_id)
                if runjob.status == RunJobStatus.CANCELLED:
                    return
                return f(*args, **kwargs)
            return wrapped_f
        return wrap

    elif method_type == 'run':
        def wrap(f):
            @functools.wraps(f)
            def wrapped_f(*args, **kwargs):
                runjob_id = args[2]
                runjob = RunJob.objects.get(pk=runjob_id)
                if runjob.status == RunJobStatus.CANCELLED:
                    return
                return f(*args, **kwargs)
            return wrapped_f
        return wrap


@if_runjob_not_cancelled('on_success')
def default_on_success(self, retval, task_id, args, kwargs):
    # create thumbnails and set runjob status to HAS_FINISHED after successfully processing an image object.
    result = Result.objects.get(pk=retval)
    result.run_job.status = RunJobStatus.HAS_FINISHED
    result.run_job.error_summary = ""
    result.run_job.error_details = ""
    save_instance(result.run_job)

    res = create_thumbnails.s(result)
    res.link(processed.s())
    res.apply_async()


def add_error_information_to_runjob(self, runjob, exc, einfo):
    # Any job using the default_on_failure method can define an error_information
    # method, which will take in an exception and a traceback string,
    # and return a dictionary containing 'error_summary' and 'error_details'.
    # This is to allow pretty formatting of error messages in the client.
    # If any StandardError is raised in the process of retrieving the
    # values, the default values are used for both fields.
    try:
        err_info = self.error_information(exc, einfo.traceback)
        err_summary = err_info['error_summary']
        err_detail = err_info['error_details']
        if rodan_settings.TRACEBACK_IN_ERROR_DETAIL:
            err_detail = str(err_detail) + "\n\n" + str(einfo.traceback)
    except StandardError as e:
        print "The error_information method is not implemented properly (or not implemented at all). Exception: "
        print "%s: %s" % (e.__class__.__name__, e.__str__())
        print "Using default sources for error information."
        err_summary = exc.__class__.__name__
        err_detail = einfo.traceback

    runjob.error_summary = err_summary
    runjob.error_details = err_detail
    save_instance(runjob)


@if_runjob_not_cancelled('on_failure')
def default_on_failure(self, exc, task_id, args, kwargs, einfo):
    runjob_id = args[1]
    runjob = RunJob.objects.get(pk=runjob_id)
    runjob.status = RunJobStatus.FAILED
    save_instance(runjob)

    add_error_information_to_runjob(self, runjob, exc, einfo)
