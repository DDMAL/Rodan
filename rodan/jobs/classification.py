from rodan.models.jobs import JobType, JobBase
from tasks import tasks


class Classifier(JobBase):
    name = 'Gamera classifier'
    slug = 'classifier'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.XML
    description = 'Performs classification on a binarized staff-less image and outputs an xml file'
    show_during_wf_create = True
    parameters = {
    }
    task = tasks.classifier
