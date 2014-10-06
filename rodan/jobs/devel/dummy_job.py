from django.conf import settings
from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.jobs.devel.celery_task import dummy_automatic_job, dummy_manual_job


def load_dummy_automatic_job():
    name = 'rodan.jobs.devel.dummy_automatic_job'
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

        ipt = InputPortType(job=j,
                            name='dummy input port type',
                            resource_type=settings.IMAGE_TYPES,
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name='dummy output port type',
                             resource_type=settings.IMAGE_TYPES,
                             minimum=1,
                             maximum=1)
        opt.save()


def load_dummy_manual_job():
    name = 'rodan.jobs.devel.dummy_manual_job'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Andrew Hankinson",
                description="A Dummy Job for testing the Job loading and workflow system",
                settings=[{'default': None, 'has_default': False, 'name': "mask", 'pixel_types': (0), 'type': "imagetype"},
                          {'default': [], 'has_default': False, 'name': "reference_histogram", 'list_of': False, 'length': -1, 'type': "floatvector"}],
                enabled=True,
                category="Dummy",
                interactive=True
                )
        j.save()

        ipt = InputPortType(job=j,
                            name='dummy input port type',
                            resource_type=settings.IMAGE_TYPES,
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name='dummy output port type',
                             resource_type=settings.IMAGE_TYPES,
                             minimum=1,
                             maximum=1)
        opt.save()
