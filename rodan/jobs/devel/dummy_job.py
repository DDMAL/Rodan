from rodan.models import Job, InputPortType, OutputPortType, ResourceType
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

        i1 = InputPortType(job=j,
                      name='in_typeA',
                      minimum=0,
                      maximum=10)
        i1.save()
        i1.resource_types.add(*ResourceType.list('test_type', 'test_type2'))

        i2 = InputPortType(job=j,
                      name='in_typeB',
                      minimum=0,
                      maximum=10)
        i2.save()
        i2.resource_types.add(*ResourceType.list('test_type', 'test_type2'))

        o1 = OutputPortType(job=j,
                       name='out_typeA',
                       minimum=0,
                       maximum=10)
        o1.save()
        o1.resource_types.add(*ResourceType.list('test_type', 'test_type2'))

        o2 = OutputPortType(job=j,
                       name='out_typeB',
                       minimum=0,
                       maximum=10)
        o2.save()
        o2.resource_types.add(*ResourceType.list('test_type', 'test_type2'))


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

        i1 = InputPortType(job=j,
                      name='in_typeA',
                      minimum=0,
                      maximum=10)
        i1.save()
        i1.resource_types.add(*ResourceType.list('test_type', 'test_type2'))

        i2 = InputPortType(job=j,
                      name='in_typeB',
                      minimum=0,
                      maximum=10)
        i2.save()
        i2.resource_types.add(*ResourceType.list('test_type', 'test_type2'))

        o1 = OutputPortType(job=j,
                       name='out_typeA',
                       minimum=0,
                       maximum=10)
        o1.save()
        o1.resource_types.add(*ResourceType.list('test_type', 'test_type2'))

        o2 = OutputPortType(job=j,
                       name='out_typeB',
                       minimum=0,
                       maximum=10)
        o2.save()
        o2.resource_types.add(*ResourceType.list('test_type', 'test_type2'))
