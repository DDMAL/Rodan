import os
import shutil

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
from rodan.settings import GAMERA_XML
from rodan.helpers.exceptions import UnknownClassifierError


class ClassificationTaskBase(Task):

    def get_classifier(self, url):
        uuid = taskutil.get_uuid_from_url(url)
        try:
            return Classifier.objects.get(pk=uuid)
        except Classifier.DoesNotExist:
            raise UnknownClassifierError("No classifier with the given uuid found.")

    def save_result(self, glyphs_model, runjob):
        result = taskutil.init_result(runjob)
        with open(glyphs_model.file_path) as f:
            taskutil.save_file_field(result.result, 'pageglyphs.xml', File(f))
        result.result_type = GAMERA_XML
        taskutil.save_instance(result)
        return result

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

            runjob = RunJob.objects.get(pk=runjob_id)
            taskutil.set_running(runjob)
            page_url = taskutil.get_page_url(runjob, result_id)
            settings = taskutil.get_settings(runjob)

            init_gamera()
            task_image = load_image(page_url)
            pageglyphs_instance = self.process_image(task_image, settings)
            result = self.save_result(pageglyphs_instance, runjob)
            return str(result.uuid)

    def on_success(self, retval, task_id, args, kwargs):
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        taskutil.save_instance(result.run_job)

    on_failure = taskutil.default_on_failure


class ManualClassificationTask(ClassificationTaskBase):
    max_retries = None
    name = 'gamera.custom.neume_classification.manual_classification'
    settings = [{'default': None, 'has_default': False, 'name': 'classifier', 'type': 'uuid_classifier'},
                {'default': None, 'has_default': False, 'name': 'pageglyphs', 'type': 'uuid_pageglyphs', 'visibility': False},
                {'default': 1, 'has_default': True, 'rng': (1, 1048576), 'name': 'num_k', 'type': 'int'},
                {'default': 4, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'max_parts_per_group', 'type': 'int'},
                {'default':  16, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'max_graph_size', 'type': 'int'},
                {'default': 2, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'max_grouping_distance', 'type': 'int'}]

    def preconfigure_settings(self, page_url, settings):
        init_gamera()
        task_image = load_image(page_url)
        classifier_model = self.get_classifier(settings['classifier'])
        rdn_pageglyph = PageGlyphs(classifier=classifier_model)
        taskutil.save_instance(rdn_pageglyph)

        temp_xml_path = taskutil.create_temp_path(ext='xml')
        gamera.gamera_xml.glyphs_to_xml(temp_xml_path,
                                        task_image.cc_analysis(),
                                        with_features=True)
        with open(temp_xml_path) as f:
            taskutil.save_file_field(rdn_pageglyph.xml_file, 'page_glyphs.xml', File(f))
        shutil.rmtree(os.path.dirname(temp_xml_path))

        rdn_pageglyph.add_uuids_and_sort_glyphs()

        return {'pageglyphs': u"{0}".format(rdn_pageglyph.get_absolute_url())}

    def process_image(self, task_image, settings):
        return PageGlyphs.objects.get(pk=settings['pageglyphs'])


class AutoClassificationTask(ClassificationTaskBase):
    max_retries = None
    name = 'gamera.custom.neume_classification.automatic_classification'
    settings = [{'default': 1, 'has_default': True, 'rng': (1, 1048576), 'name': 'num_k', 'type': 'int'},
                {'default': 4, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'max_parts_per_group', 'type': 'int'},
                {'default': 16, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'max_graph_size', 'type': 'int'},
                {'default': 16, 'has_default': True, 'rng': (1, 1048576), 'name': 'distance_threshold', 'type': 'int'},
                {'default': None, 'has_default': False, 'name': 'classifier', 'type': 'uuid_classifier'},
                {'default': None, 'has_default': False, 'name': 'pageglyphs', 'type': 'uuid_pageglyphs', 'visibility': False}]

    def save_glyphs(self, glyphs, classifier):
        pageglyphs_instance = PageGlyphs(classifier=classifier)
        taskutil.save_instance(pageglyphs_instance)
        temp_xml_path = taskutil.create_temp_path(ext='xml')
        gamera.gamera_xml.glyphs_to_xml(temp_xml_path, glyphs, with_features=True)

        with open(temp_xml_path) as f:
            taskutil.save_file_field(pageglyphs_instance.xml_file, 'page_glyphs.xml', File(f))
        shutil.rmtree(os.path.dirname(temp_xml_path))

        pageglyphs_instance.add_uuids_and_sort_glyphs()

        return pageglyphs_instance

    def process_image(self, task_image, settings):
        classifier_model = self.get_classifier(settings['classifier'])
       # Is there a way to do a dropdown menu or a checkbox menu in the client instrea of using features='all'?
        cknn = gamera.knn.kNNNonInteractive(classifier_model.file_path,
                                            features='all', perform_splits=True,
                                            num_k=settings['num_k'])
        func = gamera.classify.BoundingBoxGroupingFunction(settings['distance_threshold'])
        ccs = task_image.cc_analysis()
        grouped_glyphs = cknn.group_and_update_list_automatic(ccs,
                                                              grouping_function=func,
                                                              max_parts_per_group=settings['max_parts_per_group'],
                                                              max_graph_size=settings['max_graph_size'])
        cknn.generate_features_on_glyphs(grouped_glyphs)
        pageglyphs_instance = self.save_glyphs(grouped_glyphs, classifier_model)

        return pageglyphs_instance
