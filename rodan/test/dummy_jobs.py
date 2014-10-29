import os, sys, shutil
from celery import task
from django.core.files import File
from rodan.models import Input, Output
from rodan.jobs.base import RodanTask

class dummy_automatic_job(RodanTask):
    name = "rodan.jobs.devel.dummy_automatic_job"
    author = "Andrew Hankinson"
    description = "A Dummy Job for testing the Job loading and workflow system"
    settings = (
        {'default': None, 'has_default': False, 'name': "mask", 'pixel_types': (0), 'type': "imagetype"},
        {'default': [], 'has_default': False, 'name': "reference_histogram", 'list_of': False, 'length': -1, 'type': "floatvector"}
    )
    enabled = True
    category = "Dummy"
    interactive = False

    input_port_types = (
        {'name': 'in_typeA', 'minimum': 0, 'maximum': 10, 'resource_type': ('test/a1', 'test/a2')},
        {'name': 'in_typeB', 'minimum': 0, 'maximum': 10, 'resource_type': ('test/a1', 'test/a2')},
    )
    output_port_types = (
        {'name': 'out_typeA', 'minimum': 0, 'maximum': 10, 'resource_type': ('test/a1', 'test/a2')},
        {'name': 'out_typeB', 'minimum': 0, 'maximum': 10, 'resource_type': ('test/a1', 'test/a2')},
    )

    def run_my_task(self, inputs, settings, outputs):
        in_resources = []
        for ipt_name in inputs:
            for input in inputs[ipt_name]:
                in_resources.append(input['resource_path'])
        for opt_name in outputs:
            for output in outputs[opt_name]:
                if len(in_resources) > 0:
                    with open(in_resources[0], 'r') as f:
                        if 'fail' in f.read():
                            raise Exception('dummy manual job error')
                    shutil.copyfile(in_resources[0], output['resource_path'])
                else:
                    with open(output['resource_path'], 'w') as g:
                        g.write('dummy')

    def error_information(self, exc, traceback):
        return {'error_summary': "dummy automatic job error",
                'error_details': ''
            }

class dummy_manual_job(RodanTask):
    name = "rodan.jobs.devel.dummy_manual_job"
    author = "Andrew Hankinson"
    description = "A Dummy Job for testing the Job loading and workflow system"
    settings = (
        {'default': None, 'has_default': False, 'name': "mask", 'pixel_types': (0), 'type': "imagetype"},
        {'default': [], 'has_default': False, 'name': "reference_histogram", 'list_of': False, 'length': -1, 'type': "floatvector"}
    )
    enabled = True
    category = "Dummy"
    interactive = False

    input_port_types = (
        {'name': 'in_typeA', 'minimum': 0, 'maximum': 10, 'resource_type': ('test/a1', 'test/a2')},
        {'name': 'in_typeB', 'minimum': 0, 'maximum': 10, 'resource_type': ('test/a1', 'test/a2')},
    )
    output_port_types = (
        {'name': 'out_typeA', 'minimum': 0, 'maximum': 10, 'resource_type': ('test/a1', 'test/a2')},
        {'name': 'out_typeB', 'minimum': 0, 'maximum': 10, 'resource_type': ('test/a1', 'test/a2')},
    )

    def run_my_task(self, inputs, settings, outputs):
        in_resources = []
        for ipt_name in inputs:
            for input in inputs[ipt_name]:
                in_resources.append(input['resource_path'])

        for opt_name in outputs:
            for output in outputs[opt_name]:
                if len(in_resources) > 0:
                    with open(in_resources[0], 'r') as f:
                        if 'fail' in f.read():
                            raise Exception('dummy manual job error')
                    shutil.copyfile(in_resources[0], output['resource_path'])
                else:
                    with open(output['resource_path'], 'w') as g:
                        g.write('dummy')

    def error_information(self, exc, traceback):
        return {'error_summary': "dummy manual job error",
                'error_details': ''
            }
