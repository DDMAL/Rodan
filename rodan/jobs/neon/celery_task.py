import os
import shutil
from PIL import Image
from rodan.jobs.util import taskutil
from rodan.models.runjob import RunJob, RunJobStatus
from rodan.models.result import Result
from rodan.jobs.neon.utils import live_mei_path, backup_mei_path, live_mei_directory, compressed_image_path
from rodan.jobs.base import RodanTask


class PitchCorrectionTask(RodanTask):
    max_retries = None
    name = "neon.pitch_correction"
    settings = []   # This job really doesn't have any settings.

    def _create_temp_neon_directory(self, runjob):
        temp_path = live_mei_directory(runjob)
        if os.path.exists(temp_path):
            print "A neon temp path directory was already in the runjob path."
            print "Overwriting directory..."
            shutil.rmtree(temp_path)
        os.mkdir(temp_path)

    def run_task(self, result_id, runjob_id, *args, **kwargs):
        runjob = RunJob.objects.get(pk=runjob_id)

        if runjob.needs_input:
            if runjob.status == RunJobStatus.RUN_ONCE_WAITING:
                self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

            else:
                # This is the first time the job is running.
                taskutil.set_running(runjob)
                page_path = runjob.page.compat_file_path

                self._create_temp_neon_directory(runjob)
                mei_path = taskutil.get_input_path(runjob, result_id)
                shutil.copy(mei_path, live_mei_path(runjob))
                shutil.copy(live_mei_path(runjob), backup_mei_path(runjob))

                page_image = Image.open(page_path)
                page_image.save(compressed_image_path(runjob), quality=40)

                taskutil.set_run_once_waiting(runjob)
                self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

        else:
            taskutil.set_running(runjob)
            result = taskutil.init_result(runjob)
            taskutil.save_result(result, live_mei_path(runjob))
            return str(result.uuid)

    @taskutil.if_runjob_not_cancelled('on_success')
    def on_success(self, retval, task_id, args, kwargs):
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        taskutil.save_instance(result.run_job)

    on_failure = taskutil.default_on_failure
