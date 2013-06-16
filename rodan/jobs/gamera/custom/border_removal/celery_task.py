from rodan.jobs.gamera.custom.gamera_custom_base import GameraCustomTask
from rodan.jobs.gamera import argconvert
from gamera.core import init_gamera
from gamera.toolkits.border_removal.plugins.border_removal import border_removal
import Image
import ImageDraw
from gamera.plugins.pil_io import from_pil


class AutoBorderRemovalTask(GameraCustomTask):
    max_retries = None
    name = 'gamera.custom.border_removal.auto_border_removal'
    settings = argconvert.convert_arg_list(border_removal.args.list)

    def process_image(self, task_image, settings):
        init_gamera()
        grey_image = task_image.to_greyscale()
        crop_mask = grey_image.border_removal(**settings)
        result_image = task_image.mask(crop_mask)

        return result_image


class CropBorderRemovalTask(GameraCustomTask):
    max_retries = None
    name = 'gamera.custom.border_removal.crop_border_removal'

    # Ideally, Border Removal Settings should not be coupled with rdn_crop settings.
    # Need more robust argument system. To-Do. This is ugly.
    from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop
    settings = argconvert.convert_arg_list(rdn_crop.args.list)

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

    def process_image(self, task_image, settings):
        init_gamera()
        crop_mask = CropBorderRemovalTask.create_mask(task_image, **settings)
        result_image = task_image.mask(crop_mask)

        return result_image
