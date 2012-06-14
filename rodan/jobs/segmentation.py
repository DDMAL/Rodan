import json

from PIL import Image, ImageDraw, ImageMath

import utils
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs='tiff')
def segment(image_filepath, **kwargs):
    input_img = Image.open(image_filepath)

    # make a '1' bit image with the same size as the input_img
    mask_img = Image.new('1', input_img.size)

    # instantiate an ImageDraw object using the mask_img object
    mask_drawer = ImageDraw.Draw(mask_img)

    # get the JSON data and load it as a string
    json_poly_data = json.loads(kwargs['JSON'])
    image_width = kwargs['imw']
    for polygon in json_poly_data:
        flattened_poly = [j for i in polygon for j in i]
        for val in flattened_poly:
            
        mask_drawer.polygon(flattened_poly, outline=1, fill=1)

    output_img = ImageMath.eval("~(a - b)", a=input_img, b=mask_img)
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
    description = 'Segments an image based on polygon definitions in json.'
    show_during_wf_create = True
    parameters = {
        'JSON': None,
        'imw': 1.0
    }
    task = segment
