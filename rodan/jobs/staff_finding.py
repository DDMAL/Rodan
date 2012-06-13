import json

import gamera.core
from gamera.toolkits import musicstaves
from gamera.gameracore import Point

import utils
from rodan.models.jobs import JobType, JobBase


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
    for poly in poly_list:
        #following condition checks if there are the same amount of points on all 4 staff lines
        if len(poly[0].vertices) == len(poly[1].vertices) and \
        len(poly[0].vertices) == len(poly[2].vertices) and \
        len(poly[0].vertices) == len(poly[3].vertices):
            continue
        else:
            for j, line in enumerate(poly):
                for k, vert in enumerate(line.vertices):
                    for m, innerline in enumerate(poly):
                        if line == innerline:
                            continue
                        if k < len(line.vertices):
                            y_pix_diff = vert.x - innerline.vertices[k].x
                        else:
                            y_pix_diff = -10000

                        if y_pix_diff < 3 and y_pix_diff > -3:
                            continue
                        else:
                            staffspace_multiplier = m - j
                            line.vertices.insert(k, Point(vert.x, vert.y + (staffspace_multiplier * staffspace_height)))

    return poly_list


@utils.rodan_task(inputs='tiff')
def find_staves(image_filepath, **kwargs):
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
    #both 0's can be parameterized, first one is staffline_height and second is staffspace_height, both default 0
    #the constructor converts to onebit if its not ONEBIT. Note that it will simply convert, no binarisation process
    staff_finder = musicstaves.StaffFinder_miyao(gamera.core.load_image(image_filepath), 0, 0)
    staff_finder.find_staves(kwargs['num_lines'], kwargs['scanlines'], kwargs['blackness'], kwargs['tolerance'])
    poly_list = staff_finder.get_polygon()

    poly_list = __fix_poly_point_list(poly_list, staff_finder.staffspace_height)

    poly_json_list = __create_polygon_outer_points_json_dict(poly_list)

    encoded = json.dumps(poly_json_list)

    return {
        'json': encoded
    }


class StaffFind(JobBase):
    name = 'Find staff lines'
    slug = 'staff-find'
    input_type = JobType.BINARISED_IMAGE
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
    is_automatic = True
