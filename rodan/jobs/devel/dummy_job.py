from rodan.models.job import Job
from rodan.jobs.devel.celery_task import dummy_job


def load_dummy_job():
    name = 'rodan.jobs.devel.dummy_job'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Andrew Hankinson",
                description="A Dummy Job for testing the Job loading and workflow system",
                settings=[{'default': None, 'has_default': False, 'name': "mask", 'pixel_types': (0), 'type': "imagetype"},
                          {'default': [], 'has_default': False, 'name': "reference_histogram", 'list_of': False, 'length': -1, 'type': "floatvector"}],
                enabled=True,
                category="Dummy",
                interactive=False
                )
        j.save()
