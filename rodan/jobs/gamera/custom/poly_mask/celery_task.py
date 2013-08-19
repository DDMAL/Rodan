import json
from gamera.core import init_gamera, load_image
from gamera.plugins.pil_io import from_pil
import Image
import ImageDraw
from rodan.jobs.gamera.custom.gamera_custom_base import GameraCustomTask


class PolyMaskTask(GameraCustomTask):
    max_retries = None
    name = 'gamera.custom.border_removal.poly_mask'

    settings = [{'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'image_width', 'type': 'int'}]

    def preconfigure_settings(self, page_url, settings):
        init_gamera()
        task_image = load_image(page_url)

        miyao_settings = settings.copy()
        del miyao_settings['image_width']

        return {'image_width': task_image.ncols}
       # return {'polygon_outer_points': poly_json_list, 'image_width': task_image.ncols}

    def process_image(self, task_image, settings):
        mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
        mask_drawer = ImageDraw.Draw(mask_img)

        try:
            polygon_data = json.loads(settings['polygon_outer_points'])
        except ValueError:
            # There's a problem in the JSON - it may be malformed, or empty
            polygon_data = []

        for polygon in polygon_data:
            flattened_poly = [j for i in polygon for j in i]
            mask_drawer.polygon(flattened_poly, outline='black', fill='black')
        del mask_drawer

        task_image_greyscale = task_image.to_greyscale()    # Because gamera masking doesn't work on one-bit images
        segment_mask = from_pil(mask_img).to_onebit()
        result_image_greyscale = task_image_greyscale.mask(segment_mask)
        result_image = result_image_greyscale.to_onebit()   # Get it back to one-bit

        return result_image
