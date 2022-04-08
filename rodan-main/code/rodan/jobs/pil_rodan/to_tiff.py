import PIL.Image
import PIL.ImageFile
from rodan.jobs.base import RodanTask

class to_tiff(RodanTask):
    name = 'TIFF'
    author = 'Ling-Xiao Yang'
    description = 'Convert image to tiff format'
    settings = {
        'job_queue': 'Python3'
    }
    enabled = True
    category = "PIL - Conversion"
    interactive = False

    input_port_types = (
        {'name': 'Image', 'minimum': 1, 'maximum': 1, 'resource_types': lambda mime: mime.startswith('image/')},
    )
    output_port_types = (
        {'name': 'TIFF Image', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/tiff']},
    )

    def run_my_task(self, inputs, settings, outputs):
        infile = inputs['Image'][0]['resource_path']
        outfile = outputs['TIFF Image'][0]['resource_path']

        image = PIL.Image.open(infile).convert('RGB')
        image.save(outfile, 'TIFF')

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
        PIL.Image.new("RGB", size=(50, 50), color=(256, 0, 0)).save(inputs['in'][0]['resource_path'], 'JPEG')
        outputs = {
            'out': [
                {'resource_type': 'image/tiff',
                 'resource_path': testcase.new_available_path()
                }
            ]
        }

        self.run_my_task(inputs, {}, outputs)
        result = PIL.Image.open(outputs['out'][0]['resource_path'])
        testcase.assertEqual(result.format, 'TIFF')
