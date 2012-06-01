from celery.task import task
from rodan.models.results import Result

from django.utils import timezone
import os
from gamera.core import *
from gamera.plugins import threshold

from gamera.toolkits import musicstaves

#####BINARISE######
@task(name="binarisation.simple_binarise")
def simple_binarise(result_id,threshold_value):
    result = Result.objects.get(pk=result_id)

    page = result.page
    image_name = page.filename.encode('ascii','ignore')

    file_name,file_extension = os.path.splitext(image_name)
    init_gamera()

    output_img = load_image("images/" + image_name).threshold(threshold_value)
    
    if not os.path.exists("resultimages"):
        os.makedirs("resultimages")

    output_path =  "resultimages/" + file_name + "_binarize_simplethresh_" + str(threshold_value) + file_extension
    save_image(output_img, output_path)

    result.end_total_time = timezone.now()
    result.save()
    

'''
    *smoothness*
      The amount of effect that parent blocks have on their children
      blocks.  Higher values will result in more smoothness between
      blocks.  Expressed as a percentage between 0.0 and 1.0.

    *max_block_size*
      The size of the largest block to determine a threshold.

    *min_block_size*
      The size of the smallest block to determine a threshold.

    *block_factor*
      The number of child blocks (in each direction) per parent block.
      For instance, a *block_factor* of 2 results in 4 children per
      parent.
'''
@task(name="binarisation.djvu_threshold")
def djvu_binarise(result_id,smoothness=0.2,max_block_size=512,min_block_size=64,block_factor=2):
    result = Result.objects.get(pk=result_id)

    page = result.page
    image_name = page.filename.encode('ascii','ignore')

    file_name,file_extension = os.path.splitext(image_name)
    init_gamera()

    output_img = load_image("images/" + image_name).djvu_threshold(smoothness,max_block_size,min_block_size,block_factor)

    if not os.path.exists("resultimages"):
        os.makedirs("resultimages")

    output_path =  "resultimages/" + file_name + "_binarize_djvu_smo" + str(smoothness) + "max" + str(max_block_size) + "min" + str(min_block_size) + "fac" + str(block_factor) + file_extension
    save_image(output_img, output_path)

    result.end_total_time = timezone.now()
    result.save()

#####FILTERS(ONLY RANK?)#####
"""
  *rank_val* (1, 2, ..., *k* * *k*)
    The rank of the windows pixels to select for the center. (k*k+1)/2 is
    equivalent to the median.

  *k* (3, 5 ,7, ...)
    The window size (must be odd).

  *border_treatment* (0, 1)
    When 0 ('padwhite'), window pixels outside the image are set to white.
    When 1 ('reflect'), reflecting boundary conditions are used.
"""
@task(name="filters.rank")
def rank_filter(result_id, rank_val, k,border_treatment):
    result = Result.objects.get(pk=result_id)

    page = result.page
    image_name = page.filename.encode('ascii','ignore')

    file_name,file_extension = os.path.splitext(image_name)
    init_gamera()

    output_img = load_image("images/" + image_name).rank(rank_val,k,border_treatment)

    if not os.path.exists("resultimages"):
        os.makedirs("resultimages")

    output_path =  "resultimages/" + file_name + "_rankfilter_rkv" + str(rank_val) + "k" + str(k) + "bt" + str(border_treatment) + file_extension
    save_image(output_img, output_path)

    result.end_total_time = timezone.now()
    result.save()


#####DESPECKLE#####
"""
  Removes connected components that are smaller than the given size.

  *size*
    The maximum number of pixels in each connected component that
    will be removed.

  This approach to finding connected components uses a pseudo-recursive
  descent, which gets around the hard limit of ~64k connected components
  per page in ``cc_analysis``.  Unfortunately, this approach is much
  slower as the connected components get large, so *size* should be
  kept relatively small.

  *size* == 1 is a special case and runs much faster, since it does not
  require recursion.
"""
@task(name="morphology.despeckle")
def despeckle(result_id,despeckle_value=100):
    result = Result.objects.get(pk=result_id)

    page = result.page
    image_name = page.filename.encode('ascii','ignore')

    file_name,file_extension = os.path.splitext(image_name)
    init_gamera()

    output_img = load_image("images/" + image_name)
    output_img.despeckle(despeckle_value)

    if not os.path.exists("resultimages"):
        os.makedirs("resultimages")

    output_path =  "resultimages/" + file_name + "_despeckle_" + str(despeckle_value) + file_extension
    save_image(output_img, output_path)

    result.end_total_time = timezone.now()
    result.save()


#####STAFF FINDING#####
'''
  *num_lines*:
    Number of lines within one staff. When zero, the number is automatically
    detected.

  *scan_lines*:
    Number of vertical scan lines for extracting candidate points.

  *blackness*:
    Required blackness on the connection line between two candidate points
    in order to consider them matching.

  *tolerance*:
    How much the vertical black runlength of a candidate point may deviate
    from staffline_height. When negative, this value is set to
    *max([2, staffline_height / 4])*.
'''
@task(name="staff_find.miyao")
def find_staves(result_id, num_lines=0, scanlines=20, blackness=0.8, tolerance=-1):
    result = Result.objects.get(pk=result_id)

    page = result.page
    image_name = page.filename.encode('ascii','ignore')

    file_name,file_extension = os.path.splitext(image_name)
    init_gamera()

    #both 0's can be parameterized, first one is staffline_height and second is staffspace_height, both default 0
    staff_finder = musicstaves.StaffFinder_miyao(load_image("images/" + image_name),0,0)
    staff_finder.find_staves(num_lines,scanlines,blackness,tolerance)
    output_img = staff_finder.show_result()

    output_path =  "resultimages/" + file_name + "_stafffind_nli" + str(num_lines) + "scl" + str(scanlines) + "blc" + str(blackness) + "tol" + str(tolerance) + file_extension
    output_img.save_tiff(output_path)

    result.end_total_time = timezone.now()
    result.save()