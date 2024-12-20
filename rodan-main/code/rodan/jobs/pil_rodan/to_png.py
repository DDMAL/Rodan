import PIL.Image
import PIL.ImageFile
from rodan.jobs.base import RodanTask

class to_png(RodanTask):
    name = 'PNG (RGB)'
    author = 'Andrew Hankinson'
    description = 'Convert image to png format'
    settings = {'job_queue': 'Python3'}
    enabled = True
    category = "PIL - Conversion"
    interactive = False

    input_port_types = (
        {'name': 'Image', 'minimum': 1, 'maximum': 1, 'resource_types': lambda mime: mime.startswith('image/')},
    )
    output_port_types = (
        {'name': 'RGB PNG Image', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgb+png']},
    )

    def run_my_task(self, inputs, settings, outputs):
        infile = inputs['Image'][0]['resource_path']
        outfile = outputs['RGB PNG Image'][0]['resource_path']

        image = PIL.Image.open(infile)

        # in case image is rgba. see more here: https://stackoverflow.com/a/9459208 
        if image.mode == "RGBA":
            image.load()
            background = PIL.Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
            background.save(outfile, "PNG")

        else: 
            image.convert('RGB').save(outfile, 'PNG')            

        return True

    def test_my_task(self, testcase):
        # [TODO] test more formats
        inputs = {
            'Image': [
                {'resource_type': 'image/jpeg',
                 'resource_path': testcase.new_available_path()
                }
            ]
        }
        PIL.Image.new("RGB", size=(50, 50), color=(256, 0, 0)).save(inputs['Image'][0]['resource_path'], 'JPEG')
        outputs = {
            'RGB PNG Image': [
                {'resource_type': 'image/rgb+png',
                 'resource_path': testcase.new_available_path()
                }
            ]
        }

        self.run_my_task(inputs, {}, outputs)
        result = PIL.Image.open(outputs['RGB PNG Image'][0]['resource_path'])

        # The format should be png
        testcase.assertEqual(result.format, 'PNG')

        # The input and output should be identical to each other
        import numpy as np
        in_array = np.asarray(PIL.Image.open(inputs['Image'][0]['resource_path']))
        out_array = np.asarray(result)
        np.testing.assert_array_equal(in_array, out_array)
