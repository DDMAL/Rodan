from gamera.plugins import image_conversion
from rodan.models.job import Job
from rodan.jobs.gamera.helpers import create_job_from_plugins


def load_module():
    print "Loading image conversion module"
    category = image_conversion.module.category
    all_jobs = Job.objects.filter(category__exact=category)
    all_names = [j.name for j in all_jobs]
    create_job_from_plugins(image_conversion.module.functions, all_names, category)
