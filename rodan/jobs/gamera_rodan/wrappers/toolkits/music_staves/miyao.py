import json, jsonschema
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from gamera.toolkits.musicstaves.stafffinder_miyao import StaffFinder_miyao
from rodan.jobs.gamera_rodan.helpers.poly_lists import fix_poly_point_list, create_polygon_outer_points_json_dict
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera_rodan.helpers.ensure_pixel_type import ensure_pixel_type

class MiyaoStaffFinder(RodanTask):
    name = 'Miyao Staff Finder'
    author = "Deepanjan Roy"
    description = 'use Miyao staff finding algorithm to detect staff lines.'
    settings = {
        'title': 'Miyao settings',
        'type': 'object',
        'required': ['Number of lines', 'Scan lines', 'Blackness', 'Tolerance'],
        'properties': {
            'Number of lines': {
                'type': 'integer',
                'default': 0,
                'minimum': -1048576,
                'maximum': 1048576,
                'description': 'Number of lines within one staff. When zero, the number is automatically detected.'
            },
            'Scan lines': {
                'type': 'integer',
                'default': 20,
                'minimum': -1048576,
                'maximum': 1048576,
                'description': 'Number of vertical scan lines for extracting candidate points.'
            },
            'Blackness': {
                'type': 'number',
                'default': 0.8,
                'minimum': -1048576,
                'maximum': 1048576,
                'description': 'Required blackness on the connection line between two candidate points in order to consider them matching.'
            },
            'Tolerance': {
                'type': 'integer',
                'default': -1,
                'minimum': -1048576,
                'maximum': 1048576,
                'description': 'How much the vertical black runlength of a candidate point may deviate from staffline_height. When negative, this value is set to *max([2, staffline_height / 4])*'
            }
        }
    }
    enabled = True
    category = "Gamera - Music Staves"
    interactive = False 

    input_port_types = [{
        'name': 'Greyscale or one-bit PNG image',
        'resource_types': ['image/onebit+png','image/greyscale+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'PNG image (Miyao results used as mask)',
        'resource_types': ['image/onebit+png','image/greyscale+png'],
        'minimum': 0,
        'maximum': 2
    },
    {
        'name': 'Polygons (Miyao results)',
        'resource_types': ['application/gamera-polygons+txt'],
        'minimum': 0,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):

        task_image = load_image(inputs['Greyscale or one-bit PNG image'][0]['resource_path'])
        staff_finder = StaffFinder_miyao(task_image, 0, 0)

        fn_kwargs = {
            'num_lines': settings['Number of lines'],
            'scanlines': settings['Scan lines'],
            'blackness': settings['Blackness'],
            'tolerance': settings['Tolerance'],
        }
        staff_finder.find_staves(**fn_kwargs)

        poly_list = staff_finder.get_polygon()
        poly_list = fix_poly_point_list(poly_list, staff_finder.staffspace_height)
        poly_json_list = create_polygon_outer_points_json_dict(poly_list)

        # If poly output, save it
        if 'Polygons (Miyao results)' in outputs:
            poly_string = str(poly_json_list)
            f = open(outputs['Polygons (Miyao results)'][0]['resource_path'], 'w')
            f.write(poly_string)
            f.close()
       
        # If image output, save it
        if 'PNG image (Miyao results used as mask)' in outputs:
            mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
            mask_drawer = ImageDraw.Draw(mask_img)
            for polygon in poly_json_list:
                flattened_poly = [j for i in polygon for j in i]
                mask_drawer.polygon(flattened_poly, outline='black', fill='black')
            del mask_drawer
            task_image_rgb = task_image.to_rgb()    #Because gamera masking doesn't work on onebit or grey16 images.
            segment_mask = from_pil(mask_img).to_onebit()
            result_image_rgb = task_image_rgb.mask(segment_mask)
            result_image = ensure_pixel_type(result_image_rgb, outputs['PNG image (Miyao results used as mask)'][0]['resource_type'])
            for i in range(len(outputs['PNG image (Miyao results used as mask)'])):
                result_image.save_PNG(outputs['PNG image (Miyao results used as mask)'][i]['resource_path'])
