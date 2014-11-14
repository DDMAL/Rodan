from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from gamera.core import load_image
from gamera.toolkits.border_removal.plugins.border_removal import border_removal
from PIL import Image
from PIL import ImageDraw
from gamera.plugins.pil_io import from_pil


class AutoBorderRemovalTask(RodanTask):
    name = 'gamera.custom.border_removal.auto_border_removal'
    author = "Deepanjan Roy"
    description = "Automatically tries to remove the border of a page. Non-interactive."
    settings = argconvert.convert_arg_list(border_removal.args.list)
    enabled = True
    category = "Border Removal"
    interactive = False

    input_port_types = [{
        'name': 'input',
        'resource_types': ('image/onebit+png', 'image/greyscale+png', 'image/rgb+png'),
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ('image/onebit+png', 'image/greyscale+png', 'image/rgb+png'),
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
        """
        settings = argconvert.convert_to_gamera_settings(rodan_job_settings)
        task_image = load_image(inputs['input'][0]['resource_path'])
        grey_image = task_image.to_greyscale()
        crop_mask = grey_image.border_removal(**settings)

        need_to_change_back = False
        if task_image.data.pixel_type == 0:
            task_image = task_image.to_greyscale()
            need_to_change_back = True

        result_image = task_image.mask(crop_mask)

        if need_to_change_back:
            result_image = result_image.to_onebit()

        result_image.save_image(outputs['output'][0]['resource_path'])

class CropBorderRemovalTask(RodanTask):
    name = 'gamera.custom.border_removal.crop_border_removal'
    author = "Deepanjan Roy"
    description = "Manual masking crop. Uses the crop interface. Interactive."

    # Ideally, Border Removal Settings should not be coupled with rdn_crop settings.
    # Need more robust argument system. [TODO]. This is ugly.
    from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop
    settings = argconvert.convert_arg_list(rdn_crop.args.list)

    enabled = True
    category = "Border Removal"
    interactive = False

    input_port_types = [{
        'name': 'input',
        'resource_types': ('image/onebit+png', 'image/greyscale+png', 'image/rgb+png'),
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ('image/onebit+png', 'image/greyscale+png', 'image/rgb+png'),
        'minimum': 1,
        'maximum': 1
    }]

    @staticmethod
    def create_mask(org_img, ulx=0, uly=0, lrx=0, lry=0, imw=0):

        if 0 == imw:
            scale_factor = 1
        else:
            scale_factor = float(org_img.ncols) / float(imw)

        arg_ulx = scale_factor * ulx
        arg_uly = scale_factor * uly
        arg_lrx = scale_factor * lrx - 1
        arg_lry = scale_factor * lry - 1

        if arg_ulx < 0:
            arg_ulx = 0
        if arg_ulx > org_img.ncols:
            arg_ulx = org_img.ncols

        if arg_lrx < 0:
            arg_lrx = 0
        if arg_lrx > (org_img.ncols - 1):
            arg_lrx = org_img.ncols - 1

        if arg_uly < 0:
            arg_uly = 0
        if arg_uly > org_img.nrows:
            arg_uly = org_img.nrows

        if arg_lry < 0:
            arg_lry = 0
        if arg_lry > (org_img.nrows - 1):
            arg_lry = org_img.nrows - 1

        im = Image.new('L', (org_img.ncols, org_img.nrows), color='white')
        draw = ImageDraw.Draw(im)
        draw.rectangle((arg_ulx, arg_uly, arg_lrx, arg_lry), fill='black')
        del draw

        im = from_pil(im)
        return im.to_onebit()


    def run_my_task(self, inputs, rodan_job_settings, outputs):
        """
        Note that if the incoming image is onebit, it will convert it to greyscale,
        do the cropping, and then convert it back to onebit. This can sometimes
        lead to unexpected behavior, especially because converting to greyscale
        can do some interpolation, and converting back to onebit uses a default
        binarizaiton algorithm (the otsu threshold). These can change the image.
        """
        settings = argconvert.convert_to_gamera_settings(rodan_job_settings)
        task_image = load_image(inputs['input'][0]['resource_path'])

        need_to_change_back = False
        if task_image.data.pixel_type == 0:
            task_image = task_image.to_greyscale()
            need_to_change_back = True

        crop_mask = CropBorderRemovalTask.create_mask(task_image, **settings)
        result_image = task_image.mask(crop_mask)

        if need_to_change_back:
            result_image = result_image.to_onebit()

        result_image.save_image(outputs['output'][0]['resource_path'])
