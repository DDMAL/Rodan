import json
from rodan.jobs.utils import rodan_task, load_image_for_job
from rodan.celery_models.jobtype import JobType
from rodan.celery_models.jobbase import JobBase


import gamera.gamera_xml
import gamera.core
gamera.core.init_gamera()
from aomr_resources.AomrObject import AomrObject
from aomr_resources.AomrMeiOutput import AomrMeiOutput
from aomr_resources.AomrExceptions import AomrUnableToFindStavesError


@rodan_task(inputs=('xml'), others=['segmented_image', 'page_sequence'])
def pitch_find(xml_filepath, segmented,  page_sequence, **kwargs):
    # Run a rank filter on the image to make the staves bigger
    #  for pitch detection
    print "loading image... performing rank filter"
    input_image = load_image_for_job(segmented, gamera.plugins.misc_filters.rank)
    # XXX: Parameters to change?
    rank_image = input_image.rank(9, 9, 0)

    #gamera.core.save_image(rank_image, "aomr2-rank.tiff")
    print "... done. Finding pitches"
    try:
        aomr_obj = AomrObject(rank_image, \
            discard_size=kwargs['discard_size'],
            lines_per_staff=4,
            staff_finder=0,
            staff_removal=0,
            binarization=0)
        glyphs = gamera.gamera_xml.glyphs_from_xml(xml_filepath)

        recognized_glyphs = aomr_obj.run(glyphs)

        data = json.loads(recognized_glyphs)
        mei_file = AomrMeiOutput(data, str(segmented), str(page_sequence))
    except AomrUnableToFindStavesError as e:
        #if something goes wrong, this will create an empty mei file (instead of crashing)
        print e
        mei_file = AomrMeiOutput({}, str(segmented), str(page_sequence))
    print "... done. Writing MEI"

    return {
        'mei': mei_file
    }


class PitchFindingFull(JobBase):
    """ Perform pitch finding by doing the staff recognition in the job, not outside """
    name = 'Pitch finding (image input)'
    slug = 'pitch-finding-full'
    input_type = JobType.CLASSIFY_XML
    output_type = JobType.MEI
    description = 'Find the pitches of neumes on an image.'
    show_during_wf_create = True
    enabled = False
    parameters = {
        'discard_size': 12
    }
    task = pitch_find
    is_automatic = True
    outputs_image = False
