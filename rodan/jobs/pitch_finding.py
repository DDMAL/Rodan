from gamera import gamera_xml

import utils
from aomr_resources.AomrObject import AomrObject
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs=('tiff', 'xml'))
def pitch_find(image_filepath, xml_filepath, **kwargs):
    aomr_obj = AomrObject(image_filepath, \
        discard_size=kwargs['discard_size'],
        lines_per_staff=4,
        staff_finder=0,
        staff_removal=0,
        binarization=0)
    glyphs = gamera_xml.glyphs_from_xml(xml_filepath)
    recognized_glyphs = aomr_obj.run(glyphs)

    return {
        'json': recognized_glyphs
    }


class PitchFinding(JobBase):
    name = 'Pitch finding'
    slug = 'pitch-finding'
    input_type = JobType.CLASSIFY_XML
    output_type = JobType.PITCH_JSON
    description = 'Finds the pitchs of a given image using the output of classification on that image. Returns a .json file containing all the information'
    show_during_wf_create = True
    parameters = {
        'discard_size': 12
    }
    task = pitch_find
    is_automatic = True
