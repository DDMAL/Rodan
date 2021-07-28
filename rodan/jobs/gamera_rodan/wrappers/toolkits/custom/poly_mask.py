import json
import os
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera_rodan.helpers.ensure_pixel_type import ensure_pixel_type
from rodan.settings import MEDIA_URL, MEDIA_ROOT

def media_file_path_to_public_url(media_file_path):
    chars_to_remove = len(MEDIA_ROOT)
    return os.path.join(MEDIA_URL, media_file_path[chars_to_remove:])

class PolyMask(RodanTask):
    name = 'Manual Polygon Masking'
    author = "Ling-Xiao Yang"
    description = "Interactive interface to create polygon masks"
    settings = {}
    enabled = True
    category = "Gamera - Masking"
    interactive = True

    input_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/onebit+png', 'image/greyscale+png', 'image/grey16+png', 'image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    },
    {
        'name': 'Polygons',
        'resource_types': ['application/gamera-polygons+txt'],
        'minimum': 0,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'PNG image (masked)',
        'resource_types': ['image/onebit+png', 'image/greyscale+png', 'image/grey16+png', 'image/rgb+png'],
        'minimum': 0,
        'maximum': 1
    },
    {
        'name': 'Polygons',
        'resource_types': ['application/gamera-polygons+txt'],
        'minimum': 0,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        if '@polygon_outer_points' not in settings:
            task_image = load_image(inputs['PNG image'][0]['resource_path'])
            polygon_outer_points = '[]'
            if 'Polygons' in inputs:
                with open(inputs['Polygons'][0]['resource_path'], 'r') as myfile:
                    polygon_outer_points = myfile.read().replace('\n', '')
            settings_update = {'@image_width': task_image.ncols, '@polygon_outer_points': polygon_outer_points}
            return self.WAITING_FOR_INPUT(settings_update)
        else:
            polygon_outer_points = settings['@polygon_outer_points']

            # If image output port, write image
            if 'PNG image (masked)' in outputs:
                task_image = load_image(inputs['PNG image'][0]['resource_path'])

                mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
                mask_drawer = ImageDraw.Draw(mask_img)

                for polygon in polygon_outer_points:
                    flattened_poly = [j for i in polygon for j in i]
                    mask_drawer.polygon(flattened_poly, outline='black', fill='black')
                del mask_drawer

                task_image_rgb = task_image.to_rgb()    # Because gamera masking doesn't work on onebit or grey16 images.
                segment_mask = from_pil(mask_img).to_onebit()
                result_image_rgb = task_image_rgb.mask(segment_mask)
                result_image = ensure_pixel_type(result_image_rgb, outputs['PNG image (masked)'][0]['resource_type'])

                result_image.save_PNG(outputs['PNG image (masked)'][0]['resource_path'])

            # If polygons image output port, write poly file
            if 'Polygons' in outputs:
                poly_string = str(polygon_outer_points)
                f = open(outputs['Polygons'][0]['resource_path'], 'w')
                f.write(poly_string)
                f.close()

    def get_my_interface(self, inputs, settings):
	image_path = inputs['PNG image'][0]['resource_path']
        interface = 'interfaces/poly_mask.html'
        data = {
            'image_url': media_file_path_to_public_url(image_path),
            'image_width': settings['@image_width'],
            'polygon_outer_points': settings['@polygon_outer_points']
        }
        return (interface, data)

    def validate_my_user_input(self, inputs, settings, user_input):
        if 'polygon_outer_points' not in user_input:
            raise self.ManualPhaseException("Bad data")
        # [TODO] validate userdata
        return {'@polygon_outer_points': user_input['polygon_outer_points']}
