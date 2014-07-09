from rodan.models.job import Job
from rodan.jobs.devel.celery_task import dummy_job


def load_dummy_job():
    name = 'rodan.jobs.devel.dummy_job'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Andrew Hankinson",
                description="A Dummy Job for testing the Job loading and workflow system",
                settings=[{}],
                enabled=True,
                category="Dummy",
                interactive=False
                )
        j.save()
