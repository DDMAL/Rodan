import json, jsonschema
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from gamera.toolkits.musicstaves.stafffinder_miyao import StaffFinder_miyao
from rodan.jobs.gamera.custom.segmentation.poly_lists import fix_poly_point_list, create_polygon_outer_points_json_dict
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from rodan.jobs.gamera.base import ensure_pixel_type

class Segmentation(RodanTask):
    name = 'gamera.segmentation.segmentation'
    author = "Deepanjan Roy"
    description = "Finds the staves using Miyao Staff Finder and masks out everything else"
    settings = {
        'type': 'object',
        'required': ['num_lines', 'scanlines', 'blackness', 'tolerance','manual'],
        'properties': {
            'num_lines': {
                'type': 'integer',
                'default': 0,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'scanlines': {
                'type': 'integer',
                'default': 20,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'blackness': {
                'type': 'number',
                'default': 0.8,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'tolerance': {
                'type': 'integer',
                'default': -1,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'manual': {
                'type': 'boolean',
                'default': 'false'
            }
        }
    }
    enabled = True
    category = "Segmentation"
    interactive = True 

    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/onebit+png','image/greyscale+png','image/grey16+png','image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ['image/onebit+png','image/greyscale+png','image/grey16+png','image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        if not settings.get('manual'):
            task_image = load_image(inputs['input'][0]['resource_path'])

            #ranked_page = task_image.rank(9, 9, 0)
            staff_finder = StaffFinder_miyao(task_image, 0, 0)

            fn_kwargs = {
                'num_lines': settings.get('@num_lines', settings['num_lines']),
                'scanlines': settings.get('@scanlines', settings['scanlines']),
                'blackness': settings.get('@blackness', settings['blackness']),
                'tolerance': settings.get('@tolerance', settings['tolerance']),
            }
            staff_finder.find_staves(**fn_kwargs)

            poly_list = staff_finder.get_polygon()
            poly_list = fix_poly_point_list(poly_list, staff_finder.staffspace_height)
            poly_json_list = create_polygon_outer_points_json_dict(poly_list)

            settings.update({'@polygon_outer_points': poly_json_list})

            mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
            mask_drawer = ImageDraw.Draw(mask_img)

            for polygon in settings['@polygon_outer_points']:
                flattened_poly = [j for i in polygon for j in i]
                mask_drawer.polygon(flattened_poly, outline='black', fill='black')
            del mask_drawer

            #task_image_greyscale = task_image.to_greyscale()    # Because gamera masking doesn't work on one-bit images        
            task_image_rgb = task_image.to_rgb()    #Because gamera masking doesn't work on onebit or grey16 images.
            segment_mask = from_pil(mask_img).to_onebit()
            #result_image_greyscale = task_image_greyscale.mask(segment_mask)
            #result_image = result_image_greyscale.to_onebit()   # Get it back to one-bit
            result_image_rgb = task_image_rgb.mask(segment_mask)
            result_image = ensure_pixel_type(result_image_rgb, outputs['output'][0]['resource_type'])
            
            result_image.save_PNG(outputs['output'][0]['resource_path'])

        elif not settings.get('@polygon_outer_points'):
            task_image = load_image(inputs['input'][0]['resource_path'])

            #ranked_page = task_image.rank(9, 9, 0)
            staff_finder = StaffFinder_miyao(task_image, 0, 0)

            fn_kwargs = {
                'num_lines': settings.get('@num_lines', settings['num_lines']),
                'scanlines': settings.get('@scanlines', settings['scanlines']),
                'blackness': settings.get('@blackness', settings['blackness']),
                'tolerance': settings.get('@tolerance', settings['tolerance']),
            }
            staff_finder.find_staves(**fn_kwargs)

            poly_list = staff_finder.get_polygon()
            poly_list = fix_poly_point_list(poly_list, staff_finder.staffspace_height)
            poly_json_list = create_polygon_outer_points_json_dict(poly_list)

            settings_update = {
                '@image_width': task_image.ncols,
                '@polygon_outer_points': poly_json_list
            }
            return self.WAITING_FOR_INPUT(settings_update)
        else:
            task_image = load_image(inputs['input'][0]['resource_path'])
            mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
            mask_drawer = ImageDraw.Draw(mask_img)

            for polygon in settings['@polygon_outer_points']:
                flattened_poly = [j for i in polygon for j in i]
                mask_drawer.polygon(flattened_poly, outline='black', fill='black')
            del mask_drawer

            #task_image_greyscale = task_image.to_greyscale()    # Because gamera masking doesn't work on one-bit images        
            task_image_rgb = task_image.to_rgb()    #Because gamera masking doesn't work on onebit or grey16 images.
            segment_mask = from_pil(mask_img).to_onebit()
            #result_image_greyscale = task_image_greyscale.mask(segment_mask)
            #result_image = result_image_greyscale.to_onebit()   # Get it back to one-bit
            result_image_rgb = task_image_rgb.mask(segment_mask)
            result_image = ensure_pixel_type(result_image_rgb, outputs['output'][0]['resource_type'])
            
            result_image.save_PNG(outputs['output'][0]['resource_path'])

    def get_my_interface(self, inputs, settings):
        t = 'interfaces/segmentation.html'
        c = {
            'image_url': inputs['input'][0]['large_thumb_url'],
            'polygon_outer_points': settings['@polygon_outer_points'],
            'image_width': settings['@image_width'],
            'settings': {
                'num_lines': settings.get('@num_lines', settings['num_lines']),
                'scanlines': settings.get('@scanlines', settings['scanlines']),
                'blackness': settings.get('@blackness', settings['blackness']),
                'tolerance': settings.get('@tolerance', settings['tolerance']),
            }
        }
        return (t, c)

    def validate_my_user_input(self, inputs, settings, user_input):
        if 'new_settings' in user_input:
            # update settings
            new_settings = user_input['new_settings']
            v = jsonschema.Draft4Validator(self.settings)
            try:
                v.validate(new_settings)
            except jsonschema.exceptions.ValidationError as e:
                raise self.ManualPhaseException(e.message)
            return {
                '@polygon_outer_points': None,    # let computer do it again
                '@num_lines': new_settings['num_lines'],
                '@scanlines': new_settings['scanlines'],
                '@blackness': new_settings['blackness'],
                '@tolerance': new_settings['tolerance'],
            }
        else:
            # store result
            points = user_input['polygon_outer_points']
            # [TODO] validate input
            return {'@polygon_outer_points': points}
