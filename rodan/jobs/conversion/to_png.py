import PIL.Image
import PIL.ImageFile
from rodan.jobs.base import RodanAutomaticTask

class to_png(RodanAutomaticTask):
    name = 'rodan.jobs.conversion.to_png'
    author = 'Andrew Hankinson'
    description = 'Convert image to png format'
    settings = ()
    enabled = True
    category = "Conversion"

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
