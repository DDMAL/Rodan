#import json
from gamera.core import init_gamera, load_image
#from gamera.plugins.pil_io import from_pil
#import Image
#import ImageDraw
from rodan.jobs.gamera.custom.gamera_custom_base import GameraCustomTask


class PixelSegmentTask(GameraCustomTask):
    max_retries = None
    name = 'gamera.custom.lyric_extraction.pixel_segment'

    settings = [{'visibility': False, 'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'image_width', 'type': 'int'},
                {'visibility': False, 'default': None, 'has_default': True, 'name': 'polygon_outer_points', 'type': 'json'}]

    def preconfigure_settings(self, page_url, settings):
        init_gamera()
        task_image = load_image(page_url)
        miyao_settings = settings.copy()
        del miyao_settings['image_width']
        return {'image_width': task_image.ncols}

    def process_image(self, task_image, settings):
        return task_image
