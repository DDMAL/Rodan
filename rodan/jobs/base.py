from celery import Task
from rodan.models.runjob import RunJob, RunJobStatus
from rodan.jobs.util import taskutil
from rodan.helpers.thumbnails import create_thumbnails
from rodan.helpers.processed import processed
from django.conf import settings as rodan_settings


class RodanTask(Task):
    def run(self, runjob_id):
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
