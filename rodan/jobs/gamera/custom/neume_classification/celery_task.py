from celery import Task
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.helpers.thumbnails import create_thumbnails
from gamera.core import init_gamera, load_image
from rodan.jobs.util import taskutil
import gamera.core
import gamera.gamera_xml
import gamera.classify
import gamera.knn
from gamera import classify

JOB_NAME_MANUAL = 'gamera.custom.neume_classification.manual_classification'


class ManualClassificationTask(Task):
    max_retries = None
    name = 'gamera.custom.neume_classification.manual_classification'


    def run(self, result_id, runjob_id, *args, **kwargs):
        runjob = RunJob.objects.get(pk=runjob_id)
        runjob.status = RunJobStatus.RUNNING
        runjob.save()

        if runjob.needs_input:
            runjob.status = RunJobStatus.WAITING_FOR_INPUT
            runjob.save()
            self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

        runjob.status = RunJobStatus.RUNNING
        runjob.save()

        print "The job received input."

    def on_success(self, retval, task_id, args, kwargs):
        # create thumbnails and set runjob status to HAS_FINISHED after successfully processing an image object.
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        result.run_job.save()

        res = create_thumbnails.s(result)
        res.apply_async()

    def on_failure(self, *args, **kwargs):
        runjob = RunJob.objects.get(pk=args[2][1])  # index into args to fetch the failed runjob instance
        runjob.status = RunJobStatus.FAILED
        runjob.save()


class NonInteractiveClassificationTask(Task):
    max_retries = None
    name = 'gamera.custom.neume_classification.automatic_classification'
    settings = [{'default':1,'has_default':True,'rng':(1,1048576),'name':'num_k','type':'int'},
                {'default':4,'has_default':True,'rng':(-1048576,1048576),'name':'max_parts_per_group','type':'int'},
                {'default':16,'has_default':True,'rng':(-1048576,1048576),'name':'max_graph_size','type':'int'},
                {'default':-1,'has_default':True,'rng':(-1048576,1048576),'name':'tolerance','type':'int'},
                {'default': None,'has_default':True,'name':'polygon_outer_points','type':'json'},
                {'default': 0,'has_default':True,'rng':(-1048576,1048576),'name':'image_width','type':'int'}]

    def process_image(task_image, settings):
        # Code borrowed from the old rodan classification job.
        
        # Is there a way to do a dropdown menu or a checkbox menu in the client instrea of using features='all'?
        cknn = gamera.knn.kNNNonInteractive(settings.CLASSIFIER_XML, features='all', perform_splits=True, num_k=settings[num_k])
        func = gamera.classify.BoundingBoxGroupingFunction(2)
        ccs = task_image.cc_analysis()
#
        cs_image = cknn.group_and_update_list_automatic(ccs,
                                                        grouping_function=func,
                                                        max_parts_per_group=4,
                                                        max_graph_size=16)
#
        cknn.generate_features_on_glyphs(cs_image)
        return gamera.gamera_xml.WriteXMLFile(glyphs=cs_image, with_features=True)
#
#
    def run(self, result_id, runjob_id, *args, **kwargs):
        runjob = RunJob.objects.get(pk=runjob_id)
        taskutil.set_running(runjob)
        page_url = taskutil.get_page_url(runjob, result_id)
        settings = taskutil.get_settings(runjob)
#
        init_gamera()
        task_image = load_image(page_url)
        result_xml = self.process_image(task_image, settings)
#
#
#
        result = taskutil.save_result_as_png(result_image, runjob)
        return str(result.uuid)
#
    def on_success(self, retval, task_id, args, kwargs):
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        result.run_job.save()
#
    def on_failure(self, *args, **kwargs):
        runjob = RunJob.objects.get(pk=args[2][1])  # index into args to fetch the failed runjob instance
        runjob.status = RunJobStatus.FAILED
        runjob.save()
#
