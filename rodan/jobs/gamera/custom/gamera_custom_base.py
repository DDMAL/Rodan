from celery import Task
from rodan.models.runjob import RunJob
from rodan.models.result import Result
from rodan.models.runjob import RunJobStatus
from rodan.jobs.util import taskutil
from gamera.core import init_gamera, load_image


class GameraCustomTask(Task):
    max_retries = None
    name = "gamera_custom_task__no_job_name_provided"
    settings = []

    on_success = taskutil.default_on_success
    on_failure = taskutil.default_on_failure

    def preconfigure_settings(self, page_url, settings):
        """This method returns a name-value dictionary of updates
            to preconfigure some of the settings in runjob."""

        return {}

    def process_image(self, task_image, settings):
        """This method MUST be overridden.
            It takes a gamera_image and a settings dictionary, and returns a gamera image."""

        pass

    def run(self, result_id, runjob_id, *args, **kwargs):
        """Note: Even if you decide to override the entire run method,
            make sure you load and save images with gamera methods, and not PIL methods.
            Otherwise the loaded/saved images often don't have the proper pixel types,
            and becomes unsuitable for use in a workflow with other gamera-based jobs."""

        runjob = RunJob.objects.get(pk=runjob_id)

        if runjob.needs_input:
            if runjob.status == RunJobStatus.RUN_ONCE_WAITING:
                self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

            else:
                # This is the first time the job is running.
                taskutil.set_running(runjob)
                page_url = taskutil.get_page_url(runjob, result_id)
                settings = taskutil.get_settings(runjob)

                updates = self.preconfigure_settings(page_url, settings)
                taskutil.apply_updates(runjob, updates)

                taskutil.set_run_once_waiting(runjob)
                self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

        else:
            taskutil.set_running(runjob)
            page_url = taskutil.get_page_url(runjob, result_id)
            settings = taskutil.get_settings(runjob)

            init_gamera()
            task_image = load_image(page_url)
            result_image = self.process_image(task_image, settings)

            result = taskutil.save_result_as_png(result_image, runjob)
            return str(result.uuid)
