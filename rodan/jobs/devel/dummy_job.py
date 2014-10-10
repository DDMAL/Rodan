from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.jobs.devel.celery_task import dummy_automatic_job, dummy_manual_job
from rodan.models.resource import ResourceType

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

        InputPortType(job=j,
                      name='in_typeA',
                      resource_type=ResourceType.IMAGE_TYPES,
                      minimum=0,
                      maximum=10).save()
        InputPortType(job=j,
                      name='in_typeB',
                      resource_type=ResourceType.IMAGE_TYPES,
                      minimum=0,
                      maximum=10).save()

        OutputPortType(job=j,
                       name='out_typeA',
                       resource_type=ResourceType.IMAGE_TYPES,
                       minimum=0,
                       maximum=10).save()
        OutputPortType(job=j,
                       name='out_typeB',
                       resource_type=ResourceType.IMAGE_TYPES,
                       minimum=0,
                       maximum=10).save()


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

        InputPortType(job=j,
                      name='in_typeA',
                      resource_type=ResourceType.IMAGE_TYPES,
                      minimum=0,
                      maximum=10).save()
        InputPortType(job=j,
                      name='in_typeB',
                      resource_type=ResourceType.IMAGE_TYPES,
                      minimum=0,
                      maximum=10).save()

        OutputPortType(job=j,
                       name='out_typeA',
                       resource_type=ResourceType.IMAGE_TYPES,
                       minimum=0,
                       maximum=10).save()
        OutputPortType(job=j,
                       name='out_typeB',
                       resource_type=ResourceType.IMAGE_TYPES,
                       minimum=0,
                       maximum=10).save()
