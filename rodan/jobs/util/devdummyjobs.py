from rodan.models.job import Job

def load_wfjobuuid():
    name = 'dummywfuuidjob'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Deepanjan Roy",
                description="Classifies the neumes detected in the page using the classifier interface.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (1,), "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (1,), "name": "output"},
                settings=[{'default': None, 'has_default': False, 'type': 'uuid_workflowjob', 'name': 'Auxilary Input'}],
                enabled=True,
                category="Dummy",
                interactive=False
                )

        j.save()