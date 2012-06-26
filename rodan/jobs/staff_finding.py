import json

import gamera.core
import gamera.toolkits.musicstaves

import utils
from rodan.models.jobs import JobType, JobBase


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
    staff_finder = gamera.toolkits.musicstaves.StaffFinder_miyao(gamera.core.load_image(image_filepath), 0, 0)
    staff_finder.find_staves(kwargs['num_lines'], kwargs['scanlines'], kwargs['blackness'], kwargs['tolerance'])
    poly_list = staff_finder.get_polygon()

    poly_list = utils.fix_poly_point_list(poly_list, staff_finder.staffspace_height)

    poly_json_list = utils.create_polygon_outer_points_json_dict(poly_list)

    stafffind_json_list = utils.create_json_from_poly_list(poly_list)

    encoded1 = json.dumps(poly_json_list)
    encoded2 = json.dumps(stafffind_json_list)

    return {
        'json': encoded1,
        'json2': encoded2,
    }


class StaffFinding(JobBase):
    name = 'Staff Finding'
    slug = 'staff-finding'
    input_type = JobType.RANKED_IMAGE
    output_type = JobType.POLYGON_JSON
    description = 'Retrieves and outputs polygon point coordinates information contouring staves in json format.'
    show_during_wf_create = True
    parameters = {
        'num_lines': 0,
        'scanlines': 20,
        'blackness': 0.8,
        'tolerance': -1
    }
    task = find_staves
    is_automatic = True
    outputs_image = False
