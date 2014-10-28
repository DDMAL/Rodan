import PIL.Image
import PIL.ImageFile
from rodan.jobs.base import RodanTask

class to_png(RodanTask):
    name = 'rodan.jobs.conversion.to_png'
    def run_my_task(self, inputs, settings, outputs):
        infile = inputs['in'][0]['resource_path']
        outfile = outputs['out'][0]['resource_path']

        image = PIL.Image.open(infile).convert('RGB')
        image.save(outfile, 'PNG')

        return True
