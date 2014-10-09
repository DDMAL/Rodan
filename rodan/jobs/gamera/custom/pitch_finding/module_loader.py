from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.jobs.gamera.custom.pitch_finding.celery_task import PitchFindingTask
from rodan.models.resource import ResourceType

GAMERA_XML, MEI = ResourceType.GAMERA_XML, ResourceType.MEI


def load_pitch_finder():
    task_class = PitchFindingTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Classifies the neumes detected in the page using the classifier interface.",
                settings=task_class.settings,
                enabled=True,
                category="Pitch Finding",
                interactive=False
                )

        j.save()

        ipt = InputPortType(job=j,
                            name="input",
                            resource_type=[GAMERA_XML],
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name="output",
                             resource_type=[MEI],
                             minimum=1,
                             maximum=1)
        opt.save()


def load_module():
    load_pitch_finder()
