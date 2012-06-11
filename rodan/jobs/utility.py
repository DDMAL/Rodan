import os
import gamera.core
from rodan.models import Result, Page


def create_result_output_dirs(full_output_path):
    output_dir = os.path.dirname(full_output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def create_thumbnails(output_img, page):
    page.scale_value = 100. / max(output_img.ncols, output_img.nrows)
    scale_img_s = output_img.scale(page.scale_value, 0)
    scale_img_l = output_img.scale(page.scale_value * 10, 0)
    scale_img_s.save_PNG(page.get_path_to_image('small'))
    scale_img_l.save_PNG(page.get_path_to_image('large'))