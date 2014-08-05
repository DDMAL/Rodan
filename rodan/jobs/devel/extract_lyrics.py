from rodan.models.job import Job
from rodan.jobs.devel.celery_task import dummy_job


def load_dummy_job():
    description = """
                    **lyricline_extraction** (``Image`` [OneBit] *binarization*)
                    Removes stafflines and extract lyriclines.
                    Note: no post-processing to extract precise posistion of each lyric or deal with overlapping situation is applied.
                    *binarization* image after border removal and binarization.
                    For best performance, scale the image around 1000*1000 to 2000*2000
                  """
    name = 'rodan.jobs.devel.extract_lyrics'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Ruth Berkow",
                description=description,
                settings=[{'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'num_lines', 'type': 'int'},
                          {'default': 5, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'scanlines', 'type': 'int'}],
                enabled=True,
                category="Border and Lyric Extraction",
                interactive=False
                )
        j.save()
