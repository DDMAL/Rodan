
import json
import os

#from gamera.core import *
from gamera import gamera_xml
from gamera.classify import BoundingBoxGroupingFunction
from gamera.plugins import threshold, transformation
from gamera.toolkits import musicstaves
from gamera.knn import kNNNonInteractive
from gamera.gameracore import Point

from celery.task import task
from django.conf import settings
from django.utils import timezone
from rodan.models.results import Result, Parameter, ResultFile
from rodan.models.jobs import JobType


def __setup_task(result_id):
    global result
    result = Result.objects.get(pk=result_id)

    page = result.page
    image_name = page.filename.encode('ascii','ignore')

    init_gamera()
    return image_name

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


# def __fix_poly_point_list(poly_list, staffspace_height):
#     debug_string = ''
#     for poly in poly_list:#loop over polygons
#         debug_string += "\nPOLYGON\n"
#         #following condition checks if there are the same amount of points on all 4 staff lines
#         if len(poly[0].vertices) == len(poly[1].vertices) and \
#         len(poly[0].vertices) == len(poly[2].vertices) and \
#         len(poly[0].vertices) == len(poly[3].vertices):
#             debug_string += "polygon is fine.\n"
#             continue
#         else:
#             debug_string += "polygon needs fixing..\n"
#             for j in xrange(0,len(poly)):#loop over all 4 staff lines
#                 debug_string += "outer loop on staff %s\n" % j
#                 for k in xrange(0,len(poly[j].vertices)):#loop over points of staff
#                     debug_string += "point %s\n" % k
#                     for l in xrange(0,len(poly)):#loop over all 4 staff lines
#                         debug_string += "inner loop on staff %s\n" % l
#                         if l == j:# optimization to not loop through the same staff line as outer loop
#                             continue

#                         if(k < len(poly[l].vertices)):
#                             y_pix_diff = poly[j].vertices[k].x - poly[l].vertices[k].x
#                         else:
#                             y_pix_diff = -10000

#                         debug_string += "y_pix_diff = %s\n" % y_pix_diff
#                         if(y_pix_diff < 5 and y_pix_diff > -5): #if the y coordinate pixel difference within acceptable deviation
#                             debug_string += "matching point found within deviation range\n"
#                             continue
#                         else:
#                             debug_string += "NO matching point found within deviation range\n"
#                             #missing a point on that staff
#                             staffspace_multiplier = (l - j) #represents the number of staff lines apart from one another
#                             poly[l].vertices.insert(k, Point(poly[j].vertices[k].x, poly[j].vertices[k].y + (staffspace_multiplier * staffspace_height)))
#                             debug_string += "current staff %s points: %s\n" % (l, poly[l].vertices)

#     return poly_list


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
def simple_binarise(result_id, threshold=0):
    result = Result.objects.get(pk=result_id)
    page = result.page.get_latest_file(JobType.IMAGE)
     
    """
    The below has been commented out because it doesn't work
    The above is for debugging
    use Page.get_latest_image() to get the abs filepath to the latest image
    Save it to MEDIA_ROOT, project_id/page_id/job_id/filename
    maybe add a method to Page to make it easier to do that?
    ====================
    """
    image_name = __setup_task(result_id)
    output_img = load_image("images/" + image_name).threshold(threshold_value)

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name =file_name + "_binarize_simplethresh_" + str(threshold_value) + file_extension

    save_image(output_img,"resultimages/" + output_file_name)
    params = {"threshold_value": threshold_value}
    result.save_parameters(**params)
    result.create_file(output_file_name)

    file = open(os.path.join(settings.MEDIA_ROOT, 'lol'), 'wt')
    file.write("lol")
    filepath = Result.objects.get(pk=result_id).page.get_latest_file(JobType.IMAGE)
    file.write(filepath)
    return filepath

@task(name="binarisation.djvu_threshold")
def djvu_binarise(result_id, smoothness=0.2, max_block_size=512, min_block_size=64, block_factor=2):
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
    result = Result.objects.get(pk=result_id)
    image_name = __setup_task(result_id)
    output_img = load_image("images/" + image_name).djvu_threshold(smoothness,max_block_size,min_block_size,block_factor)

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name = file_name + "_binarize_djvu_smo" + str(smoothness) + "max" + str(max_block_size) + "min" + str(min_block_size) + "fac" + str(block_factor) + file_extension

    save_image(output_img,"resultimages/" + output_file_name)

    params = {"smoothness": smoothness,
              "max_block_size": max_block_size,
              "min_block_size": min_block_size,
              "block_factor": block_factor
             }
    result.save_parameters(**params)
    result.create_file(output_file_name)

#####FILTERS(ONLY RANK?)#####

@task(name="filters.rank")
def rank_filter(result_id, rank_val, k, border_treatment):
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
    result = Result.objects.get(pk=result_id)
    image_name = __setup_task(result_id)
    output_img = load_image("images/" + image_name).rank(rank_val,k,border_treatment)

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name = file_name + "_rankfilter_rkv" + str(rank_val) + "k" + str(k) + "bt" + str(border_treatment) + file_extension

    save_image(output_img,"resultimages/" + output_file_name)

    params = {"rank_val": rank_val,
              "k": k,
              "border_treatment": border_treatment
             }
    result.save_parameters(**params)
    result.create_file(output_file_name)


#####DESPECKLE#####
@task(name="morphology.despeckle")
def despeckle(result_id, despeckle_value=100, **params):
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
    image_name = __setup_task(result_id)

    output_img = load_image("images/%s" % image_name)
    output_img.despeckle(despeckle_value)

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name = "%s_despeckle_%s%s" % (filename, str(despeckle_value) + file_extension)

    save_image(output_img,"resultimages/" + output_file_name)

    result.save_parameters(**params)
    result.create_file(output_file_name)

#####STAFF FINDING#####

@task(name="staff_find.miyao")
def find_staves(result_id, num_lines=0, scanlines=20, blackness=0.8, tolerance=-1):
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
    image_name = __setup_task(result_id)

    #both 0's can be parameterized, first one is staffline_height and second is staffspace_height, both default 0
    staff_finder = musicstaves.StaffFinder_miyao(load_image("images/" + image_name),0,0)
    staff_finder.find_staves(num_lines,scanlines,blackness,tolerance)
    poly_list = staff_finder.get_polygon()
    with open("resultimages/test/before.txt","w") as f:
        f.write(__print_poly_list(poly_list))

    poly_list = __fix_poly_point_list(poly_list,staff_finder.staffspace_height)
    with open("resultimages/test/after.txt","w") as f:
        f.write(__print_poly_list(poly_list))

    # poly_json_list = __create_polygon_json_dict(poly_list)

    # encoded = json.dumps(poly_json_list)

    # output_file_name ="resultimages/json/" + image_name + "_stdata.json"
    # with open(output_file_name,"w") as f:
    #     f.write(encoded)

    params = {"smoothness": smoothness,
              "max_block_size": max_block_size,
              "min_block_size": min_block_size,
              "block_factor": block_factor
             }
    result.save_parameters(**params)
    result.create_file(output_file_name)
    __save_results(output_file_name,num_lines=num_lines,scanlines=scanlines,blackness=blackness,tolerance=tolerance)

######CLASSIFICATION######
@task(name="classifier")
def classifier(result_id):
    image_name = __setup_task(result_id)

    cknn = kNNNonInteractive("optimized_classifier_31Jan.xml",'all',True,1) #will be replaced by a new classifier that will be created soon

    ccs = load_image("images/" + image_name).cc_analysis()
    func = BoundingBoxGroupingFunction(4)

    cs_image = cknn.group_and_update_list_automatic(ccs,grouping_function=func,max_parts_per_group=4,max_graph_size=16)

    cknn.generate_features_on_glyphs(cs_image)
    myxml = gamera_xml.WriteXMLFile(glyphs=cs_image,with_features=True)
    output_file_name = image_name + "_cl.xml"
    myxml.write_filename("resultimages/xml/" + output_file_name)


    params = {"smoothness": smoothness,
              "max_block_size": max_block_size,
              "min_block_size": min_block_size,
              "block_factor": block_factor
             }
    result.save_parameters(**params)
    result.create_file(output_file_name)
    __save_results(output_file_name)


#####TRANSFORMATION#####
@task(name="rotate")
def rotate(result_id,angle):
    image_name = __setup_task(result_id)

    output_img = load_image("images/" + image_name).rotate(angle)

    file_name,file_extension = os.path.splitext(image_name)
    output_file_name = file_name + "_rotate_" + str(angle) + file_extension

    output_img.save_image("resultimages/" + output_file_name)

    params = {"smoothness": smoothness,
              "max_block_size": max_block_size,
              "min_block_size": min_block_size,
              "block_factor": block_factor
             }
    result.save_parameters(**params)
    result.create_file(output_file_name)
    __save_results(output_file_name,angle=angle)
