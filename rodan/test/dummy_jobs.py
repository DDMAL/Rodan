import os, sys, shutil, json
from celery import task
from django.core.files import File
from rodan.models import Input, Output
from rodan.jobs.base import RodanTask
from django.template import Template
from rest_framework import status

class dummy_automatic_job(RodanTask):
    name = "rodan.jobs.devel.dummy_automatic_job"
    author = "Andrew Hankinson"
    description = "A Dummy Job for testing the Job loading and workflow system"
    settings = {
        'type': 'object',
        'required': ['a', 'b'],
        'properties': {
            'a': {
                'type': 'integer',
                'minimum': 0,
            },
            'b': {
                'type': 'array',
                'items': {'type': 'number'}
            }
        }
    }
    enabled = True
    category = "Dummy"
    interactive = False

    input_port_types = (
        {'name': 'in_typeA', 'minimum': 0, 'maximum': 10, 'resource_types': ('test/a1', 'test/a2')},
        {'name': 'in_typeB', 'minimum': 0, 'maximum': 10, 'resource_types': ('test/a1', 'test/a2')},
    )
    output_port_types = (
        {'name': 'out_typeA', 'minimum': 0, 'maximum': 10, 'resource_types': ('test/a1', 'test/a2')},
        {'name': 'out_typeB', 'minimum': 0, 'maximum': 10, 'resource_types': ('test/a1', 'test/a2')},
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
                        if 'fail' in f.read():   # You can deliberately fail the job in test
                            raise Exception('dummy manual job error')
                    shutil.copyfile(in_resources[0], output['resource_path'])
                else:
                    with open(output['resource_path'], 'w') as g:
                        g.write('dummy')

    def my_error_information(self, exc, traceback):
        return {'error_summary': "dummy automatic job error",
                'error_details': ''
            }

class dummy_manual_job(RodanTask):
    name = "rodan.jobs.devel.dummy_manual_job"
    author = "Andrew Hankinson"
    description = "A Dummy Job for testing the Job loading and workflow system"
    settings = {
        'type': 'object',
        'required': ['a', 'b'],
        'properties': {
            'a': {
                'type': 'integer',
                'minimum': 0,
            },
            'b': {
                'type': 'array',
                'items': {'type': 'number'}
            }
        }
    }
    enabled = True
    category = "Dummy"
    interactive = True

    input_port_types = (
        {'name': 'in_typeA', 'minimum': 0, 'maximum': 10, 'resource_types': ('test/a1', 'test/a2')},
        {'name': 'in_typeB', 'minimum': 0, 'maximum': 10, 'resource_types': ('test/a1', 'test/a2')},
    )
    output_port_types = (
        {'name': 'out_typeA', 'minimum': 0, 'maximum': 10, 'resource_types': ('test/a1', 'test/a2')},
        {'name': 'out_typeB', 'minimum': 0, 'maximum': 10, 'resource_types': ('test/a1', 'test/a2')},
    )

    def run_my_task(self, inputs, settings, outputs):
        if '@finish' not in settings:
            return self.WAITING_FOR_INPUT()
        else:
            for opt in outputs:
                for o in outputs[opt]:
                    with open(o['resource_path'], 'w') as f:
                        json.dump(settings['@finish'], f)

    def get_my_interface(self, inputs, settings):
        t = Template("dummy {{test}}")
        if 'in_typeA' in inputs and len(inputs['in_typeA']) > 0:
            with open(inputs['in_typeA'][0]['resource_path'], 'r') as f:
                c = json.load(f)
        else:
            c = {}
        return (t, c)

    def validate_my_user_input(self, inputs, settings, user_input):
        if 'fail' in user_input:   # You can deliberately fail the job in test
            raise self.ManualPhaseException('dummy manual job error')
        else:
            return {'@finish': user_input}
