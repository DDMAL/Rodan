import json

import gamera.gamera_xml

import utils
from aomr_resources.AomrObject import AomrObject
from aomr_resources.AomrMeiOutput import AomrMeiOutput
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs=('tiff', 'xml', 'json2'))
def pitch_find(image_filepath, xml_filepath, json2_filepath, **kwargs):
    aomr_obj = AomrObject(image_filepath, \
        discard_size=kwargs['discard_size'],
        lines_per_staff=4,
        staff_finder=0,
        staff_removal=0,
        binarization=0)
    glyphs = gamera.gamera_xml.glyphs_from_xml(xml_filepath)

    json_data = open(json2_filepath)
    encoded_poly_list = json.load(json_data)
    poly_list = utils.create_poly_list_from_json(encoded_poly_list)

    recognized_glyphs = aomr_obj.run(glyphs, poly_list)
    mei_file = AomrMeiOutput(recognized_glyphs, image_filepath.encode('ascii', 'ignore'), '0')  # the 0 at the end is wrong, its suppose to be page number (whatever that means, waiting for gabriels response)

    return {
        'mei': mei_file
    }


class PitchFinding(JobBase):
    name = 'Pitch finding'
    slug = 'pitch-finding'
    input_type = JobType.CLASSIFY_XML
    output_type = JobType.MEI_UNCORRECTED
    description = 'Finds the pitchs of a given image using the output of classification on that image. Returns a .json file containing all the information'
    show_during_wf_create = True
    parameters = {
        'discard_size': 12
    }
    task = pitch_find
    is_automatic = True
    outputs_image = False
