from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.jobs.gamera.custom.staff_removal.celery_task import RTStafflineRemovalTask
from django.conf import settings

ONEBIT = settings.ONEBIT


def load_rt_staff_removal():
    task_class = RTStafflineRemovalTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Removes the staff lines usign Roach and Tatem Staffline removal algorithm.",
                settings=task_class.settings,
                enabled=True,
                category="Staff Removal",
                interactive=False
                )

        j.save()

        ipt = InputPortType(job=j,
                            name="input",
                            resource_type=[ONEBIT],
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name="output",
                             resource_type=[ONEBIT],
                             minimum=1,
                             maximum=1)
        opt.save()


def load_module():
    load_rt_staff_removal()
