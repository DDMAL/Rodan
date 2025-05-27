import os

from rodan.jobs.base import RodanTask
from celery.utils.log import get_task_logger

class SAE_binarization(RodanTask):

    name = 'SAE Binarization'
    author = 'Wanyi Lin and Khoi Nguyen'
    description = "Uses Neural Network Model to perform background removal"
    logger = get_task_logger(__name__)

    enabled = True
    category = 'SAE Binarization - remove image background'
    interactive = False

    input_port_types = [{
        'name': 'Image',
        'resource_types': lambda mime: mime.startswith('image/'),
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'RGB PNG image',
        'resource_types': ['image/rgba+png'],
        'minimum': 1,
        'maximum': 1
    }]

    settings = {'job_queue': 'GPU'}

    def run_my_task(self, inputs, settings, outputs):
        from SAE_binarization.binarize.binarize import run_binarize

        load_image_path = inputs['Image'][0]['resource_path']
        save_image_path = "{}.png".format(outputs['RGB PNG image'][0]['resource_path'])
        image_processed = run_binarize(load_image_path, save_image_path)

        os.rename(save_image_path,outputs['RGB PNG image'][0]['resource_path'])
        return True

    def my_error_information(self, exc, traceback):
        return
