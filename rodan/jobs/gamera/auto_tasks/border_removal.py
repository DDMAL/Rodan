from rodan.jobs.base import RodanAutomaticTask, RodanManualTask
from rodan.jobs.gamera import argconvert
from gamera.core import load_image
from gamera import enums
from gamera.toolkits.border_removal.plugins.border_removal import border_removal
from PIL import Image
from PIL import ImageDraw
from gamera.plugins.pil_io import from_pil

class AutoBorderRemovalTask(RodanAutomaticTask):
    name = 'gamera.auto_task.auto_border_removal'
    author = 'Ling-Xiao Yang'
    description = 'Automatically detect and remove the border of a scanned score.'
    settings = argconvert.convert_arg_list(border_removal.args.list)
    enabled = True
    category = border_removal.module.category
    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/rgb+png', 'image/greyscale+png', 'image/grey16+png', 'image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ['image/rgb+png', 'image/greyscale+png', 'image/grey16+png', 'image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, rodan_job_settings, outputs):
        """
        Note that if the incoming image is onebit, it will convert it to greyscale,
        do the cropping, and then convert it back to onebit. This can sometimes
        lead to unexpected behavior, especially because converting to greyscale
        can do some interpolation, and converting back to onebit uses a default
        binarizaiton algorithm (the otsu threshold). These can change the image.

        Format conversion is needed because that the `border_removal` function supports
        only GREYSCALE, and `mask` function supports only GREYSCALE and RGB.
        """
        settings = argconvert.convert_to_gamera_settings(rodan_job_settings)
        task_image = load_image(inputs['input'][0]['resource_path'])

        if task_image.data.pixel_type != enums.GREYSCALE:
            grey_image = task_image.to_greyscale()
        else:
            grey_image = task_image
        crop_mask = grey_image.border_removal(**settings)

        if task_image.data.pixel_type == enums.GREYSCALE or task_image.data.pixel_type == enums.RGB:
            result_image = task_image.mask(crop_mask)
        else:
            result_image = grey_image.mask(crop_mask)
            result_image = ensure_pixel_type(result_image, outputs['output'][0]['resource_type'])

        result_image.save_PNG(outputs['output'][0]['resource_path'])
