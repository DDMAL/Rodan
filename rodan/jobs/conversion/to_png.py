from rodan.models import Job, InputPortType, OutputPortType, ResourceType
from celery_task import to_png

def load_module():
    name = 'rodan.jobs.conversion.to_png'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Andrew Hankinson",
                description="Convert image to png format",
                settings=[],
                enabled=True,
                category="Conversion",
                interactive=False
            )
        j.save()

        i = InputPortType(job=j,
                          name='in',
                          minimum=1,
                          maximum=1)
        i.save()
        i.resource_types.add(*ResourceType.cached_filter(lambda name: name.startwith('image/')))

        o = OutputPortType(job=j,
                       name='out',
                       minimum=1,
                       maximum=1)
        o.save()
        o.resource_types.add(ResourceType.cached('image/rgb+png'))
