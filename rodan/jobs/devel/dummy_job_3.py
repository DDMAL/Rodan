from rodan.models.job import Job
from rodan.jobs.devel.celery_task import dummy_job


def load_dummy_job():
    name = 'rodan.jobs.devel.dummy_job_3'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Ruth Berkow",
                description="A third Dummy Job for testing the Job loading and workflow system",
                settings=[{'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'num_lines', 'type': 'int'},
                          {'default': 5, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'scanlines', 'type': 'int'}],
                enabled=True,
                category="Dummy",
                interactive=False
                )
        j.save()
