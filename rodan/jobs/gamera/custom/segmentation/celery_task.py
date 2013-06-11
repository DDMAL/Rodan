from rodan.jobs.gamera.custom.gamera_custom_base import GameraCustomTask

from gamera.core import init_gamera, load_image
import json
import Image
import ImageDraw
from gamera.toolkits.musicstaves.stafffinder_miyao import StaffFinder_miyao
from rodan.jobs.gamera.custom.segmentation.poly_lists import fix_poly_point_list, create_polygon_outer_points_json_dict
from gamera.plugins.pil_io import from_pil


class SegmentationTask(GameraCustomTask):
    max_retries = None
    name = 'gamera.custom.segmentation.segmentation'

    settings = [{'default':0,'has_default':True,'rng':(-1048576,1048576),'name':'num lines','type':'int'},
                    {'default':5,'has_default':True,'rng':(-1048576,1048576),'name':'scanlines','type':'int'},
                    {'default':0.8,'has_default':True,'rng':(-1048576,1048576),'name':'blackness','type':'real'},
                    {'default':-1,'has_default':True,'rng':(-1048576,1048576),'name':'tolerance','type':'int'},
                    {'default': None,'has_default':True,'name':'polygon_outer_points','type':'json'},
                    {'default': 0,'has_default':True,'rng':(-1048576,1048576),'name':'image_width','type':'int'}]

    def preconfigure_settings(self, page_url, settings):
        init_gamera()
        task_image = load_image(page_url)
        ranked_page = task_image.rank(9, 9, 0)

        miyao_settings = settings.copy()
        del miyao_settings['polygon_outer_points'], miyao_settings['image_width']

        staff_finder = StaffFinder_miyao(ranked_page, 0, 0)
        staff_finder.find_staves(**miyao_settings)

        poly_list = staff_finder.get_polygon()
        poly_list = fix_poly_point_list(poly_list, staff_finder.staffspace_height)
        poly_json_list = create_polygon_outer_points_json_dict(poly_list)

        return {'polygon_outer_points': poly_json_list, 'image_width': task_image.ncols}

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
