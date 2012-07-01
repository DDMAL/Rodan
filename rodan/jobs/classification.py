import gamera.core
import gamera.gamera_xml
import gamera.classify
import gamera.knn
from django.conf import settings

import utils
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs='tiff')
def classifier(image_filepath, **kwargs):
    #will be replaced by a new classifier that will be created soon
    cknn = gamera.knn.kNNNonInteractive(settings.CLASSIFIER_XML, 'all', True, 1)

    func = gamera.classify.BoundingBoxGroupingFunction(2)
    # must be OneBit image
    input_image = gamera.core.load_image(image_filepath)
    ccs = input_image.cc_analysis()

    cs_image = cknn.group_and_update_list_automatic(ccs, \
                    grouping_function=func,
                    max_parts_per_group=4,
                    max_graph_size=16)

    cknn.generate_features_on_glyphs(cs_image)
    output_xml = gamera.gamera_xml.WriteXMLFile(glyphs=cs_image, with_features=True)

    return {
        'xml': output_xml
    }


class Classifier(JobBase):
    name = 'Gamera classifier'
    slug = 'classifier'
    input_type = JobType.NEUME_DESPECKLE_IMAGE
    output_type = JobType.CLASSIFY_XML
    description = 'Performs classification on a binarized staff-less image and outputs an xml file'
    show_during_wf_create = True
    parameters = {
    }
    task = classifier
    is_automatic = True
    outputs_image = False
