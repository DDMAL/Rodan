import json

import pymei
import gamera.core
import gamera.gamera_xml
import gamera.classify
import gamera.knn
from gamera.core import init_gamera, load_image
from celery import Task

from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.models.workflowjob import WorkflowJob
from rodan.settings import MEI
from rodan.helpers.exceptions import UUIDParseError
from rodan.jobs.util import taskutil
from rodan.jobs.gamera.custom.pitch_finding.AomrObject import AomrObject
from rodan.jobs.gamera.custom.pitch_finding.AomrMeiOutput import AomrMeiOutput
from rodan.jobs.gamera.custom.pitch_finding.AomrExceptions import AomrUnableToFindStavesError

init_gamera()

# This is mostly a wrapper around the job in old rodan.
# There are lots of room for improvement, and lots of code to clean up.
# Most probably these will be taken care of after July 1.


class PitchFindingTask(Task):
    max_retries = None
    name = 'gamera.custom.pitch_finding.find_pitches'
    settings = [{'default': None, 'has_default': False, 'name': 'segmented_image_source', 'type': 'uuid_workflowjob'},
                {'default': 2, 'has_default': True, 'rng': [1, 1048576], 'name': 'discard_size', 'type': 'int'}]

    def process_image(self, segmented_image_path, xml_filepath, settings, page_order):
        segmented_image = load_image(segmented_image_path)
        rank_image = segmented_image.rank(9, 9, 0)
        try:
            aomr_obj = AomrObject(rank_image,
                                  discard_size=settings['discard_size'],
                                  lines_per_staff=4,
                                  staff_finder=0,
                                  staff_removal=0,
                                  binarization=0)
            glyphs = gamera.gamera_xml.glyphs_from_xml(xml_filepath)
            recognized_glyphs = aomr_obj.run(glyphs)
            data = json.loads(recognized_glyphs)
            mei_file = AomrMeiOutput(data, str(segmented_image_path), str(page_order))

        except AomrUnableToFindStavesError as e:
            #if something goes wrong, this will create an empty mei file (instead of crashing)
            print e
            mei_file = AomrMeiOutput({}, segmented_image_path, str(page_order))

        return mei_file.md

    def save_result(self, runjob, mei_document):
        result = taskutil.init_result(runjob)
        temp_mei_path = taskutil.create_temp_path(ext='mei')
        pymei.write(mei_document, temp_mei_path)
        taskutil.save_result(result, temp_mei_path)

        result.result_type = MEI
        taskutil.save_instance(result)
        return result

    def _get_segmented_image_path(self, wfrun, wfjob_url, page):
        wfjob_uuid = taskutil.get_uuid_from_url(wfjob_url)
        wfjob = WorkflowJob.objects.get(pk=wfjob_uuid)

        source_runjob = RunJob.objects.get(workflow_run=wfrun, workflow_job=wfjob, page=page)
        source_result = source_runjob.result.get()

        return source_result.result.path

    def run(self, result_id, runjob_id, *args, **kwargs):
        runjob = RunJob.objects.get(pk=runjob_id)
        taskutil.set_running(runjob)
        xml_filepath = taskutil.get_input_path(runjob, result_id)   # Trouble
        settings = taskutil.get_settings(runjob)

        segmented_image_path = self._get_segmented_image_path(runjob.workflow_run,
                                                              settings['segmented_image_source'],
                                                              runjob.page)
        page_order = runjob.page.page_order

        mei_document = self.process_image(segmented_image_path, xml_filepath, settings, page_order)
        result = self.save_result(runjob, mei_document)
        return str(result.uuid)

    def on_success(self, retval, task_id, args, kwargs):
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        taskutil.save_instance(result.run_job)

    on_failure = taskutil.default_on_failure

    def error_information(self, exc, traceback):
        if isinstance(exc, RunJob.DoesNotExist):
            return {'error_summary': "Cannot get segmented image",
                    'error_details': "Did you delete and re-add any of the jobs in the workflow?"}
        if isinstance(exc, UUIDParseError):
            return {'error_summary': "Cannot locate classifier",
                     'error_details': "Did you click Save Settings?"}
