import os, sys, shutil
from celery import task
from django.core.files import File
from rodan.models import Input, Output
from rodan.jobs.base import RodanTask

class dummy_automatic_job(RodanTask):
    name = "rodan.jobs.devel.dummy_automatic_job"
    def run_my_task(self, inputs, settings, outputs):
        in_resources = []
        for ipt_name in inputs:
            for input in inputs[ipt_name]:
                in_resources.append(input['resource_path'])

        for opt_name in outputs:
            for output in outputs[opt_name]:
                with open(in_resources[0], 'r') as f:
                    if 'fail' in f.read():
                        raise Exception('dummy automatic job error')
                shutil.copyfile(in_resources[0], output['resource_path'])

    def error_information(self, exc, traceback):
        return {'error_summary': "dummy automatic job error",
                'error_details': ''
            }

class dummy_manual_job(RodanTask):
    name = "rodan.jobs.devel.dummy_manual_job"
    def run_my_task(self, inputs, settings, outputs):
        in_resources = []
        for ipt_name in inputs:
            for input in inputs[ipt_name]:
                in_resources.append(input['resource_path'])

        for opt_name in outputs:
            for output in outputs[opt_name]:
                with open(in_resources[0], 'r') as f:
                    if 'fail' in f.read():
                        raise Exception('dummy automatic job error')
                shutil.copyfile(in_resources[0], output['resource_path'])

    def error_information(self, exc, traceback):
        return {'error_summary': "dummy manual job error",
                'error_details': ''
            }
