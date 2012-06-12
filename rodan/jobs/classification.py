import gamera.core
from gamera import gamera_xml
from gamera.classify import BoundingBoxGroupingFunction
from gamera.knn import kNNNonInteractive

from celery.task import task

import utility
from rodan.models.jobs import JobType, JobBase
from rodan.models import Result


@task(name="classification.classifier")
def classifier(result_id, **kwargs):
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE_ONEBIT)

    #will be replaced by a new classifier that will be created soon
    cknn = kNNNonInteractive("optimized_classifier_31Jan.xml", 'all', True, 1)

    func = BoundingBoxGroupingFunction(4)
    # must be OneBit image
    input_image = gamera.core.load_image(page_file_name)
    ccs = input_image.cc_analysis()

    cs_image = cknn.group_and_update_list_automatic(ccs, \
                    grouping_function=func,
                    max_parts_per_group=4,
                    max_graph_size=16)

    cknn.generate_features_on_glyphs(cs_image)
    output_xml = gamera_xml.WriteXMLFile(glyphs=cs_image, with_features=True)

    #same problem as for find_staves, bad extension
    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utility.create_result_output_dirs(full_output_path)

    output_xml.write_filename("%s.xml" % full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.XML)
    result.update_end_total_time()


class Classifier(JobBase):
    name = 'Gamera classifier'
    slug = 'classifier'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.XML
    description = 'Performs classification on a binarized staff-less image and outputs an xml file'
    show_during_wf_create = True
    parameters = {
    }
    task = classifier
