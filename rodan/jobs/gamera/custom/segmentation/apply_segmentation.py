import json
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from rodan.jobs.gamera.custom.segmentation.poly_lists import fix_poly_point_list, create_polygon_outer_points_json_dict
from rodan.jobs.base import RodanTask


class ApplySegmentationTask(RodanTask):
    name = 'gamera.custom.segmentation.apply_segmentation'
    author = "Ling-Xiao Yang"
    description = "Apply segmentation."
    settings = []
    enabled = True
    category = "Segmentation"
    interactive = False

    input_port_types = [{
        'name': 'input-image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'segmentation-data',
        'resource_types': ['application/vnd.rodan.interactive.directive+json', 'application/vnd.rodan.interactive.result+json'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output-image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]


    def run_my_task(self, inputs, rodan_job_settings, outputs):
        task_image = load_image(inputs['input-image'][0]['resource_path'])
        mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
        mask_drawer = ImageDraw.Draw(mask_img)

        with open(inputs['segmentation-data'][0]['resource_path'], 'r') as f:
            polygon_data = json.loads()

        if inputs['segmentation-data'][0]['resource_type'] == 'application/vnd.rodan.interactive.directive+json':
            polygon_data = polygon_data['result']

        for polygon in polygon_data:
            flattened_poly = [j for i in polygon for j in i]
            mask_drawer.polygon(flattened_poly, outline='black', fill='black')
        del mask_drawer

        task_image_greyscale = task_image.to_greyscale()    # Because gamera masking doesn't work on one-bit images
        segment_mask = from_pil(mask_img).to_onebit()
        result_image_greyscale = task_image_greyscale.mask(segment_mask)
        result_image = result_image_greyscale.to_onebit()   # Get it back to one-bit

        result_image.save_image(outputs['output'][0]['resource_path'])
