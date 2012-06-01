from celery.decorators import task
from rodan.models.results import Result

from django.utils import timezone
import os
import gamera.core as gam
from gamera.plugins import threshold

@task(name="binarisation.simple_binarise")
def simple_binarise(result_id,threshold_value):
    result = Result.objects.get(pk=result_id)
    
    page = result.page
    image_name = page.filename.encode('ascii','ignore')

    file_name,file_extension = os.path.splitext(image_name)
    gam.init_gamera()
    simple_thresh_obj = threshold.threshold()
        
    output_img = simple_thresh_obj(gam.load_image("images/" + image_name),threshold_value)

    if not os.path.exists("resultimages"):
        os.makedirs("resultimages")

    output_path =  "resultimages/" + file_name + "_binarize_simplethresh_" + str(threshold_value) + file_extension
    gam.save_image(output_img, output_path)

    result.end_total_time = timezone.now()
    result.save()