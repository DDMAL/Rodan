import PIL.Image
import PIL.ImageFile
from rodan.jobs.base import RodanTask

class to_png(RodanTask):
    name = 'rodan.jobs.conversion.to_png'
    author = 'Andrew Hankinson'
    description = 'Convert image to png format'
    settings = {}
    enabled = True
    category = "Conversion"
    interactive = False

    input_port_types = (
        {'name': 'in', 'minimum': 1, 'maximum': 1, 'resource_types': lambda mime: mime.startswith('image/')},
    )
    output_port_types = (
        {'name': 'out', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgb+png']},
    )

    def run_my_task(self, inputs, settings, outputs):
        infile = inputs['in'][0]['resource_path']
        outfile = outputs['out'][0]['resource_path']

        image = PIL.Image.open(infile).convert('RGB')
        image.save(outfile, 'PNG')

        return True

    def test_my_task(self, testcase):
        # [TODO] test more formats
        inputs = {
            'in': [
                {'resource_type': 'image/jpeg',
                 'resource_path': testcase.new_available_path()
                }
            ]
        }
        PIL.Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['in'][0]['resource_path'], 'JPEG')
        outputs = {
            'out': [
                {'resource_type': 'image/rgb+png',
                 'resource_path': testcase.new_available_path()
                }
            ]
        }

        self.run_my_task(inputs, {}, outputs)
        result = PIL.Image.open(outputs['out'][0]['resource_path'])
        testcase.assertEqual(result.format, 'PNG')
