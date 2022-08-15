__version__ = "1.0.0"
import shutil

from rodan.jobs.base import RodanTask
from rodan.models import ResourceType


class ResourceDistributor(RodanTask):
    name = 'Resource Distributor'
    author = 'Nicky Mirfallah'
    description = 'Distributes the resource to output'
    settings = {
        'title': 'Resource Distributor setting',
        'type': 'object',
        'properties': {
            'Resource type': {
                'enum': list(map(lambda rt: str(rt.mimetype), ResourceType.objects.all())),
                'type': 'string',
                'default': 'application/octet-stream',
                'description': 'Specifies the eligible resource types for input'
            }
        }
    }
    enabled = True
    category = "Miscellaneous"
    interactive = False
    error_summary = ""
    error_details = ""

    input_port_types = (
        {
            'name': 'Resource input',
            'minimum': 1,
            'maximum': 1,
            'resource_types': map(lambda rt: str(rt.mimetype), ResourceType.objects.all())
        },
    )
    output_port_types = (
        {
            'name': 'Resource output',
            'minimum': 1,
            'maximum': 1,
            'resource_types': map(lambda rt: str(rt.mimetype), ResourceType.objects.all())
        },
    )

    def run_my_task(self, inputs, settings, outputs):
        input_type = inputs['Resource input'][0]['resource_type']
        valid_input_type_num = settings['Resource type']
        valid_input_type = self.settings['properties']['Resource type']['enum'][valid_input_type_num]  # noqa
        if input_type != valid_input_type:
            self.my_error_information(
                None,
                (
                    "Input cannot be of type {0}. Valid input set in setting is "
                    "{1}"
                ).format(input_type, valid_input_type)
            )
            return False
        outfile_path = outputs['Resource output'][0]['resource_path']
        infile_path = inputs['Resource input'][0]['resource_path']
        shutil.copyfile(infile_path, outfile_path)
        return True

    def my_error_information(self, exc, traceback):
        self.error_summary = "Resource type not valid"
        self.error_details = traceback
