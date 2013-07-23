import os
import re
import shutil
import tempfile
import uuid
from django.core.files import File
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.jobs.gamera import argconvert
from rodan.helpers.thumbnails import create_thumbnails
from rodan.settings import IMAGE_TYPES
from rodan.helpers.exceptions import InvalidFirstJobError, UUIDParseError
from rodan.helpers.processed import processed


def set_running(runjob):
    runjob.status = RunJobStatus.RUNNING
    runjob.save()


def set_run_once_waiting(runjob):
    runjob.status = runjob.status = RunJobStatus.RUN_ONCE_WAITING
    runjob.save()


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
    must be at the end of the url. It allows a slash at the end,
    but any other funny trailing character will tick it off. The
    UUID should not contain any block separator like hyphen or
    underscore - it should be 32 adjacent characters.

    Example: All of the following will return
    12345678901234567890123456abcdef as the UUID:

    asdf://idontcare.org/12345678901234567890123456abcdef
    asdf://idontcare.org/12345678901234567890123456abcdef/
    asdf://idontcare.org/1abc2319bc11234567890123deadbeef/blah/blah/12345678901234567890123456abcdef
    12345678901234567890123456abcdef

    The following will raise exceptions:

    asdf://idontcare.org/12345678901234567890123456abcde
    asdf://idontcare.org/12345678901234567890123456abcdeff
    asdf://idontcare.org/12345678901234567890123456abcdef/?cooloption=true
    asdf://idontcare.org/12345678-9012-3456-7890-123456abcdef
    12345678-9012-3456-7890-123456abcdef

    """
    url = str(url)
    re_uuid = re.compile(r'^(.*)/(?P<uuid>[0-9a-f]{32})/?$', re.IGNORECASE)
    match_object = re_uuid.match(url)

    if match_object:
        return match_object.group('uuid')

    # Last try to see if a real uuid was passed in instead of an url.
    re_no_url_uuid = re.compile(r'^(?P<uuid>[0-9a-f]{32})$', re.IGNORECASE)
    match_object = re_no_url_uuid.match(url)

    if match_object:
        return match_object.group('uuid')

    raise UUIDParseError("Unable to extract UUID from the url. Check your input or read the get_uuid_from_url function docstring.")


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
    runjob.save()


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
    result.result.save(os.path.join(result_save_path, result_file), File(f))
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


def default_on_success(self, retval, task_id, args, kwargs):
    # create thumbnails and set runjob status to HAS_FINISHED after successfully processing an image object.
    result = Result.objects.get(pk=retval)
    result.run_job.status = RunJobStatus.HAS_FINISHED
    result.run_job.error_summary = ""
    result.run_job.error_details = ""
    result.run_job.save()

    res = create_thumbnails.s(result)
    res.link(processed.s())
    res.apply_async()


def default_on_failure(self, exc, task_id, args, kwargs, einfo):
    runjob_id = args[1]
    runjob = RunJob.objects.get(pk=runjob_id)
    runjob.status = RunJobStatus.FAILED

    # Any job using the default_on_failure method can define an error_mapping
    # method, which will take in an exception and a traceback string,
    # and return a dictionary containing 'error_summary' and 'error_details'.
    # This is to allow pretty formatting of error messages in the client.
    # If any StandardError is raised in the process of retrieving the
    # values, the default values are used for both fields.
    try:
        err_info = self.error_mapping(exc, einfo.traceback)
        err_summary = err_info['error_summary']
        err_detail = err_info['error_details']
        from rodan.settings import TRACEBACK_IN_ERROR_DETAIL
        if TRACEBACK_IN_ERROR_DETAIL:
            err_detail = str(err_detail) + "\n\n" + str(einfo.traceback)
    except StandardError as e:
        print "The error_mapping method is not implemented properly (or not implemented at all). Exception: "
        print "%s: %s" % (e.__class__.__name__, e.__str__())
        print "Using default sources for error information."
        err_summary = exc.__class__.__name__
        err_detail = einfo.traceback

    runjob.error_summary = err_summary
    runjob.error_details = err_detail
    runjob.save()

# More flexible error checking code, but this will be far more painful to maintain:
#
#    try:
#        self.error_mapping
#    except NameError as e:
#        print "No error mapping defined. Using default values."
#    else:
#        try:
#            err_info = self.error_mapping(exc, einfo)
#        except StandardError as e:
#            print "Unhandled exception in error mapping function. Exception: "
#            print "%s: %s" % (e.__class__.__name__, e.__str__())
#            print "Using default values instead."
#        else:
#            try:
#                err_summary = err_info['error_summary']
#            except KeyError:
#                print "No Error summary defined by error_mapping."
#                print "Using default values."
#            try:
#                err_detail = err_info['error_details']
#            except KeyError:
#                print "No Error details defined by error_mapping."
#                print "Using default values."
