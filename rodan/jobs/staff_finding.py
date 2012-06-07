import json

import gamera.core
from gamera.toolkits import musicstaves
from gamera.gameracore import Point

from celery.task import task

import utility
from rodan.models.jobs import JobType, JobBase
from rodan.models import Result

def __create_polygon_outer_points_json_dict(poly_list):
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


    poly_json_list = __create_polygon_outer_points_json_dict(poly_list)

    encoded = json.dumps(poly_json_list)

    full_output_path = result.page.get_filename_for_job(result.job_item.job)#this will not work, we need extension information
    utility.create_result_output_dirs(full_output_path)

    with open("%s.json" % full_output_path,"w") as f: #temp fix??
        f.write(encoded)

    result.save_parameters(**kwargs)
    result.create_file(output_file_name, JobType.JSON)
    result.total_timestamp()

class StaffFind(JobBase):
    name = 'Find staff lines'
    slug = 'staff-find'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.JSON
    description = 'Retrieves and outputs staff line point coordinates information in json format.'
    show_during_wf_create = True
    parameters = {
        'num_lines': 0,
        'scanlines': 20,
        'blackness': 0.8,
        'tolerance': -1
    }
    task = find_staves