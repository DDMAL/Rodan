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

    def test_my_task(self, testcase):
        import PIL.Image
        import numpy as np
        resource_types_list = list(map(lambda rt: str(rt.mimetype), ResourceType.objects.all()))

        # Not so sure what this job is for, but I'll use image/png as the testcase.
        inputs = {
            "Resource input": [
                {
                    'resource_type': 'image/rgb+png',
                    'resource_path': testcase.new_available_path()
                }
            ]
        }
        outputs = {
            "Resource output": [
                {
                    "resource_type": "image/rgb+png",
                    "resource_path": testcase.new_available_path()
                }
            ]
        }
        settings = {
            "Resource type": resource_types_list.index("image/rgb+png")
        }
        PIL.Image.new("RGB", size=(50, 50), color=(255, 0, 0)).save(inputs['Resource input'][0]['resource_path'], 'PNG')
        array_gt = np.zeros((50, 50, 3)).astype(np.uint8)
        array_gt[:, :, 0] = 255

        self.run_my_task(inputs, settings, outputs)

        result = PIL.Image.open(outputs['Resource output'][0]['resource_path'])
        array_result = np.asarray(result)

        # This jobs only moves an input resource to a new path, so the datatype (png) and data (array) should be identical.
        # The type (png) should stays the same
        testcase.assertEqual(result.format, 'PNG')
        # and the data should be identical
        np.testing.assert_equal(array_gt, array_result)
