import os
from django.db import models
from projects.models import Workflow, Page

import gamera.core as gam
from gamera.plugins import threshold



class Result(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)

    work_flow = models.ForeignKey(Workflow)
    page = models.ForeignKey(Page)

class Rotate(models.Model):
    rotation_value = models.IntegerField()

    result = models.OneToOneField(Result)

    def __unicode__(self):
        return "Rotate Result w/ rotation_value=%s" % self.rotation_value

'''
class Crop(Job):


class Segmentation(Job):


class SegCorrection(Job):
    def do_stuff(self):
        return seg_correct_view
'''
#inherits the default behaviour and attributes from job, and adds additional information specific to this type of relationship
class binarise(models.Model):
    #TO DO: find possible parameters for a ize job
    #perhaps extend this as well for different types of binarisation jobs??
    threshold_value = models.IntegerField()

    result = models.OneToOneField(Result)

    def __unicode__(self):
        return "binarise Result w/ threshold_value=%s" % self.threshold_value

    def binarise_image(self):
        bin_page = self.result.page
        path_to_img = bin_page.path_to_image.encode('ascii','ignore') #not used for now
        image_name = bin_page.image_name.encode('ascii','ignore')

        file_name,file_extension = os.path.splitext(image_name)
        gam.init_gamera()
        simple_thresh_obj = threshold.threshold()

        if not os.path.exists("images"):
            os.makedirs("images")
        
        output_img = simple_thresh_obj(gam.load_image("images/" + image_name),self.threshold_value)

        if not os.path.exists("resultimages"):
            os.makedirs("resultimages")

        output_path =  "resultimages/" + file_name + "_binarise_simplethresh_" + str(self.threshold_value) + file_extension
        gam.save_image(output_img, output_path)

        return output_path








