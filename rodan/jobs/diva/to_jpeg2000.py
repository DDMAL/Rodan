from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.jobs.diva.celery_task import JOB_NAME
from rodan.models.resource import ResourceType

RGB, JPEG2000 = ResourceType.RGB, ResourceType.JPEG2000


def load_module():
    job = Job.objects.filter(job_name=JOB_NAME)
    if job.exists():
        return None
    else:
        j = Job(job_name=JOB_NAME,
                author="Andrew Hankinson",
                description="Converts an image to a JPEG2000 image suitable for display in Diva",
                settings={},
                enabled=True,
                category="Conversion",
                interactive=False
                )

        j.save()

        ipt = InputPortType(job=j,
                            name=None,
                            resource_type=[RGB],
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name="output",
                             resource_type=[JPEG2000],
                             minimum=1,
                             maximum=1)
        opt.save()
