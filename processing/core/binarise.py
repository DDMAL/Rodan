import gamera.core as gam
from gamera.plugins import threshold

import os 

from processing.models import Result, ResultFile, ActionParameter
from projects.models import Page

def simple_binarise_image(page,threshold_value):
        path_to_img = page.path_to_image.name.encode('ascii','ignore') #not used for now
        image_name = page.image_name.encode('ascii','ignore')

        file_name,file_extension = os.path.splitext(image_name)
        gam.init_gamera()
        simple_thresh_obj = threshold.threshold()
        
        output_img = simple_thresh_obj(gam.load_image(path_to_img + image_name),threshold_value)

        if not os.path.exists("resultimages"):
            os.makedirs("resultimages")

        output_path =  "resultimages/" + file_name + "_binarize_simplethresh_" + str(threshold_value) + file_extension
        gam.save_image(output_img, output_path)

        return output_path