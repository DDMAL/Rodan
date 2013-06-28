from rodan.models.job import Job
from rodan.jobs.gamera.custom.staff_removal.celery_task import RTStafflineRemovalTask
from rodan.settings import ONEBIT


def load_rt_staff_removal():
    task_class = RTStafflineRemovalTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Removes the staff lines usign Roach and Tatem Staffline removal algorithm.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [ONEBIT,], "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [ONEBIT,], "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Staff Removal",
                interactive=False
                )

        j.save()


def load_module():
    load_rt_staff_removal()
