import os, sys
from celery import task
from django.core.files import File
from rodan.models import Input, Output
from rodan.jobs.base import RodanTask

class dummy_automatic_job(RodanTask):
    name = "rodan.jobs.devel.dummy_automatic_job"
    def run(self, runjob_id):
        inputs = Input.objects.filter(run_job__pk=runjob_id)
        outputs = Output.objects.filter(run_job__pk=runjob_id)

        resource_file_path = inputs[0].resource.resource_file.path
        with open(resource_file_path, 'rb') as f:
            if 'fail' in f.read():
                raise Exception('Dummy automatic job fail')
            for output in outputs:
                output.resource.resource_file.save('dummy', File(f))

    def error_information(self, exc, traceback):
        return {'error_summary': "dummy automatic job error",
                'error_details': ''
            }

class dummy_manual_job(RodanTask):
    name = "rodan.jobs.devel.dummy_manual_job"
    def run(self, runjob_id):
        inputs = Input.objects.filter(run_job__pk=runjob_id)
        outputs = Output.objects.filter(run_job__pk=runjob_id)

        resource_file_path = inputs[0].resource.resource_file.path
        with open(resource_file_path, 'rb') as f:
            for output in outputs:
                output.resource.resource_file.save('dummy', File(f))
    def error_information(self, exc, traceback):
        return {'error_summary': "dummy manual job error",
                'error_details': ''
            }
