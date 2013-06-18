import os
import shutil
import tarfile

import gamera.core
import gamera.gamera_xml
import gamera.classify
import gamera.knn
from gamera.core import init_gamera, load_image
from celery import Task
from django.core.files import File

from rodan.models.classifier import Classifier
from rodan.models.pageglyphs import PageGlyphs
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.jobs.util import taskutil
from rodan.helpers.thumbnails import create_thumbnails
from rodan.settings import PACKAGE


class ManualClassificationTask(Task):
    max_retries = None
    name = 'gamera.custom.neume_classification.manual_classification'
    settings = [{'default': None,'has_default':False,'name':'classifier','type':'uuid'},
                {'default': None,'has_default':False,'name':'pageglyphs','type':'uuid'},
                {'default':1,'has_default':True,'rng':(1,1048576),'name':'num_k','type':'int'},
                {'default':4,'has_default':True,'rng':(-1048576,1048576),'name':'max_parts_per_group','type':'int'},
                {'default':16,'has_default':True,'rng':(-1048576,1048576),'name':'max_graph_size','type':'int'},
                {'default':2,'has_default':True,'rng':(-1048576,1048576),'name':'max_grouping_distance','type':'int'}]

    def preconfigure_settings(self, page_url, settings):
        init_gamera()
        task_image = load_image(page_url)

        classifier_model = Classifier.objects.get(pk=settings['classifier'])

        classifier = gamera.knn.kNNNonInteractive(classifier_model.file_path,
                                                  features='all',
                                                  perform_splits=True,
                                                  num_k=settings['num_k'])

        func = gamera.classify.BoundingBoxGroupingFunction(settings['max_grouping_distance'])
        ccs = task_image.cc_analysis()

        rdn_pageglyph = PageGlyphs(classifier=classifier_model)
        rdn_pageglyph.save()

        temp_xml_path = taskutil.create_temp_path(ext='xml')
        gamera.gamera_xml.glyphs_to_xml(temp_xml_path, ccs, with_features=True)

        with open(temp_xml_path) as f:
            rdn_pageglyph.pageglyphs_file.save('page_glyphs.xml', File(f))

        tdir = os.path.dirname(temp_xml_path)
        shutil.rmtree(tdir)

        return {'pageglyphs': u"{0}".format(rdn_pageglyph.uuid)}

    def run(self, result_id, runjob_id, *args, **kwargs):
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
            print "Now we shall package the xml and the image. Not implemented yet."


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


class AutoClassificationTask(Task):
    max_retries = None
    name = 'gamera.custom.neume_classification.automatic_classification'
    settings = [{'default':1,'has_default':True,'rng':(1,1048576),'name':'num_k','type':'int'},
                {'default':4,'has_default':True,'rng':(-1048576,1048576),'name':'max_parts_per_group','type':'int'},
                {'default':16,'has_default':True,'rng':(-1048576,1048576),'name':'max_graph_size','type':'int'},
                {'default': None,'has_default':False,'name':'classifier','type':'uuid'},
                {'default': None,'has_default':False,'name':'pageglyphs','type':'uuid'}]

    def process_image(self, task_image, settings, classifier_model):
        # Code borrowed from the old rodan classification job.

       # Is there a way to do a dropdown menu or a checkbox menu in the client instrea of using features='all'?
        cknn = gamera.knn.kNNNonInteractive(classifier_model.file_path,
                                            features='all', perform_splits=True,
                                            num_k=settings['num_k'])
        func = gamera.classify.BoundingBoxGroupingFunction(2)
        ccs = task_image.cc_analysis()

        grouped_glyphs = cknn.group_and_update_list_automatic(ccs,
                                                              grouping_function=func,
                                                              max_parts_per_group=4,
                                                              max_graph_size=16)

        cknn.generate_features_on_glyphs(grouped_glyphs)
        return grouped_glyphs

    def save_result(self, image, glyphs, classifier, runjob):
        temp_image_path = taskutil.create_temp_path(ext='png')
        image.save_image(temp_image_path)

        temp_xml_path = taskutil.create_temp_path(ext='xml')
        gamera.gamera_xml.glyphs_to_xml(temp_xml_path, glyphs, with_features=True)
        rdn_pageglyph = PageGlyphs(classifier=classifier)
        rdn_pageglyph.save()

        with open(temp_xml_path) as f:
            rdn_pageglyph.pageglyphs_file.save('page_glyphs.xml', File(f))

        temp_tar_path = taskutil.create_temp_path(ext='tar')
        with tarfile.open(temp_tar_path, 'w') as tar:
            tar.add(temp_image_path, arcname='image.png')
            tar.add(temp_xml_path, arcname='glyphs.xml')

        result = taskutil.init_result(runjob)
        taskutil.save_result(result, temp_tar_path)
        result.result_type = PACKAGE
        result.save()

        shutil.rmtree(os.path.dirname(temp_xml_path))
        shutil.rmtree(os.path.dirname(temp_image_path))

        return result

    def run(self, result_id, runjob_id, *args, **kwargs):
        runjob = RunJob.objects.get(pk=runjob_id)
        taskutil.set_running(runjob)
        page_url = taskutil.get_page_url(runjob, result_id)
        settings = taskutil.get_settings(runjob)
        classifier = Classifier.objects.get(pk=settings['classifier'])

        init_gamera()
        task_image = load_image(page_url)
        result_glyphs = self.process_image(task_image, settings, classifier)
        glyphs_model = save_glyphs(result_glyphs, classifier)
        result = self.save_result(task_image, result_glyphs, classifier, runjob)
        return str(result.uuid)

    def on_success(self, retval, task_id, args, kwargs):
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        result.run_job.save()

    def on_failure(self, *args, **kwargs):
        runjob = RunJob.objects.get(pk=args[2][1])  # index into args to fetch the failed runjob instance
        runjob.status = RunJobStatus.FAILED
        runjob.save()
