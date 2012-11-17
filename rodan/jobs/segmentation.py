import json
import gamera.core

from PIL import Image, ImageDraw, ImageMath, ImageOps

import utils
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs='tiff')
def segment(image_filepath, **kwargs):
    input_img = Image.open(image_filepath)

    # make a '1' bit image with the same size as the input_img
    mask_img = Image.new('1', input_img.size)

    # instantiate an ImageDraw object using the mask_img object
    mask_drawer = ImageDraw.Draw(mask_img)

    try:
        json_poly_data = json.loads(kwargs['JSON'])
    except ValueError:
        # There's a problem in the JSON - it may be malformed, or empty
        json_poly_data = []

    for polygon in json_poly_data:
        flattened_poly = [j for i in polygon for j in i]
        mask_drawer.polygon(flattened_poly, outline=1, fill=1)

    output_img = ImageMath.eval('b - a', a=input_img, b=mask_img)
    output_img = ImageOps.invert(output_img.convert('RGB'))

    encoded = json.dumps(json_poly_data)

    return {
        'tiff': output_img,
        'json': encoded
    }


class Segmentation(JobBase):
    name = 'Segmentation'
    slug = 'segmentation'
    input_type = JobType.POLYGON_JSON
    output_type = JobType.SEGMENTED_IMAGE
    description = 'Separate music from other material on a page (e.g., lyrics).'
    show_during_wf_create = False
    enabled = False
    parameters = {
        'JSON': '',
    }
    task = segment

    def get_context(self, page):
        latest_json_path = page.get_latest_file_path('json')
        data = open(latest_json_path)
        json_data = json.load(data)
        return {
            'width': page.latest_width,
            'json': json_data
        }
