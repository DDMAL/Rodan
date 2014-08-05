from rodan.models.job import Job
from rodan.jobs.devel.celery_task import dummy_job


def load_dummy_job():
    description = """
                    Returns the mask of lyric lines. Gathers baseline_detection, lyric_height_estimation and lyric_line_fit functions.
                    Note: no post-processing to extract precise posistion of each lyric or deal with overlapping situation is applied.
                   """
    name = 'rodan.jobs.devel.lyric_line_detection'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Ruth Berkow",
                description=description,
                settings=[{'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'num_lines', 'type': 'int'},
                          {'default': 5, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'scanlines', 'type': 'int'}],
                enabled=True,
                category="Lyric Line Extraction",
                interactive=False
                )
        j.save()
