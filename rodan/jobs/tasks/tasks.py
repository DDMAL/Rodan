
import json
import os

import gamera.core
from gamera import gamera_xml
from gamera.classify import BoundingBoxGroupingFunction
from gamera.plugins import threshold, transformation
from gamera.toolkits import musicstaves
from gamera.knn import kNNNonInteractive
from gamera.gameracore import Point

from celery.task import task
from django.conf import settings
from rodan.models.results import Result, Parameter, ResultFile
from rodan.models.jobs import JobType

def __create_polygon_json_dict(poly_list):
    '''
        The following function is used to retrieve polygon points data of the first
        and last staff lines of a particular polygon that is drawn over a staff.
        Note that we iterate through the points of the last staff line in reverse (i.e starting
        from the last point on the last staff line going to the first) - We do this to simplify
        recreating the polygon on the front-end
    '''
    poly_json_list = []

    for poly in poly_list:
        point_list_one = [(vert.x, vert.y) for vert in poly[0].vertices]
        point_list_four = [(vert.x, vert.y) for vert in poly[3].vertices]
        point_list_four.reverse()
        point_list_one.extend(point_list_four)
        poly_json_list.append(point_list_one)

    return poly_json_list

def __fix_poly_point_list(poly_list, staffspace_height):
    for poly in poly_list:#loop over polygons
        #following condition checks if there are the same amount of points on all 4 staff lines
        if len(poly[0].vertices) == len(poly[1].vertices) and \
        len(poly[0].vertices) == len(poly[2].vertices) and \
        len(poly[0].vertices) == len(poly[3].vertices):
            continue
        else:
            for j in xrange(0,len(poly)):#loop over all 4 staff lines
                for k in xrange(0,len(poly[j].vertices)):#loop over points of staff
                    for l in xrange(0,len(poly)):#loop over all 4 staff lines
                        if l == j:# optimization to not loop through the same staff line as outer loop
                            continue

                        if(k < len(poly[l].vertices)): #before doing the difference make sure index k is within indexable range of poly[l]
                            y_pix_diff = poly[j].vertices[k].x - poly[l].vertices[k].x
                        else:
                            #if it's not in range, we are missing a point since, the insertion grows the list as we go through the points
                            y_pix_diff = -10000 #arbitrary value to evaluate next condition to false and force an insert
                            
                        if(y_pix_diff < 3 and y_pix_diff > -3): #if the y coordinate pixel difference within acceptable deviation
                            continue
                        else:
                            #missing a point on that staff
                            staffspace_multiplier = (l - j) #represents the number of staff lines apart from one another
                            poly[l].vertices.insert(k, Point(poly[j].vertices[k].x, poly[j].vertices[k].y + (staffspace_multiplier * staffspace_height)))

    return poly_list

def __print_poly_list(poly_list):
    outputstring = ''
    for poly in poly_list:
        outputstring += "\nPOLYGON\n"
        for (i,staff) in enumerate(poly):
            outputstring += "STAFF:  %s\n" % i
            outputstring += str(staff.vertices) + "\n"

    return outputstring


#####BINARISE######
@task(name="binarisation.simple_binarise")
def simple_binarise(result_id, **kwargs):
    """
    The below has been commented out because it doesn't work
    The above is for debugging
    use Page.get_latest_image() to get the abs filepath to the latest image
    Save it to MEDIA_ROOT, project_id/page_id/job_id/filename
    maybe add a method to Page to make it easier to do that?
    ====================
    """
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE)

    output_img = gamera.core.load_image(page_file_name).threshold(kwargs['threshold'])

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    output_dir = os.path.dirname(full_output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    gamera.core.save_image(output_img, full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)
    result.update_end_total_time()


@task(name="binarisation.djvu_threshold")
def djvu_binarise(result_id, **kwargs):
    """
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
    """
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE)  

    output_img = gamera.core.load_image(page_file_name).djvu_threshold(kwargs['smoothness'],kwargs['max_block_size'],kwargs['min_block_size'],kwargs['block_factor'])

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name = file_name + "_binarize_djvu_smo" + str(smoothness) + "max" + str(max_block_size) + "min" + str(min_block_size) + "fac" + str(block_factor) + file_extension

    gamera.core.save_image(output_img,"resultimages/" + output_file_name)

    result.save_parameters(**kwargs)
    result.create_file(output_file_name, JobType.IMAGE_ONEBIT)
    result.total_timestamp()

#####FILTERS(ONLY RANK?)#####

@task(name="filters.rank")
def rank_filter(result_id, **kwargs):
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
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE) 

    output_img = gamera.core.load_image(page_file_name).rank(kwargs['rank_val'],kwargs['k'],kwargs['border_treatment'])

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name = file_name + "_rankfilter_rkv" + str(rank_val) + "k" + str(k) + "bt" + str(border_treatment) + file_extension

    gamera.core.save_image(output_img,"resultimages/" + output_file_name)

    result.save_parameters(**kwargs)
    result.create_file(output_file_name, JobType.IMAGE_ONEBIT) #need to specify output type in this case its the same as input but we cannot send JobType.IMAGE --> tuple
    result.total_timestamp()


#####DESPECKLE#####
@task(name="morphology.despeckle")
def despeckle(result_id, **kwargs):
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
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE_ONEBIT) 

    output_img = gamera.core.load_image(page_file_name)
    output_img.despeckle(kwargs['despeckle_value'])

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name = "%s_despeckle_%s%s" % (filename, str(despeckle_value) + file_extension)

    gamera.core.save_image(output_img,"resultimages/" + output_file_name)

    result.save_parameters(**kwargs)
    result.create_file(output_file_name, JobType.IMAGE_ONEBIT)
    result.total_timestamp()

#####STAFF FINDING#####
@task(name="staff_find.miyao")
def find_staves(result_id, **kwargs):
    """
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
    """
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE) 

    #both 0's can be parameterized, first one is staffline_height and second is staffspace_height, both default 0
    staff_finder = musicstaves.StaffFinder_miyao(gamera.core.load_image(page_file_name),0,0)
    staff_finder.find_staves(kwargs['num_lines'], kwargs['scanlines'], kwargs['blackness'], kwargs['tolerance'])
    poly_list = staff_finder.get_polygon()

    poly_list = __fix_poly_point_list(poly_list,staff_finder.staffspace_height)


    poly_json_list = __create_polygon_json_dict(poly_list)

    encoded = json.dumps(poly_json_list)

    output_file_name ="resultimages/json/" + image_name + "_stdata.json"
    with open(output_file_name,"w") as f:
        f.write(encoded)

    result.save_parameters(**kwargs)
    result.create_file(output_file_name, JobType.JSON)
    result.total_timestamp()

######CLASSIFICATION######
@task(name="classifier")
def classifier(result_id,**kwargs):
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE_ONEBIT) 

    cknn = kNNNonInteractive("optimized_classifier_31Jan.xml",'all',True,1) #will be replaced by a new classifier that will be created soon

    ccs = gamera.core.load_image(page_file_name).cc_analysis()
    func = BoundingBoxGroupingFunction(4)

    cs_image = cknn.group_and_update_list_automatic(ccs,grouping_function=func,max_parts_per_group=4,max_graph_size=16)

    cknn.generate_features_on_glyphs(cs_image)
    myxml = gamera_xml.WriteXMLFile(glyphs=cs_image,with_features=True)
    output_file_name = image_name + "_cl.xml"
    myxml.write_filename("resultimages/xml/" + output_file_name)


    result.save_parameters(**kwargs)
    result.create_file(output_file_name,JobType.XML)
    result.total_timestamp()

#####TRANSFORMATION#####
@task(name="rotate")
def rotate(result_id,**kwargs):
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE) 

    output_img = gamera.core.load_image(page_file_name).rotate(kwargs['angle'])

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name = file_name + "_rotate_" + str(angle) + file_extension

    output_img.gamera.core.save_image("resultimages/" + output_file_name)

    result.save_parameters(**kwargs)
    result.create_file(output_file_name, JobType.IMAGE_ONEBIT) #same problem as for rank filter, need more specific output type
    result.total_timestamp()
