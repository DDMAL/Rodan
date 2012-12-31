from gamera.plugins import binarization
from rodan.models.job import Job
from rodan.jobs.gamera.helpers import create_job_from_plugins


def load_module():
    print "Loading binarization module"
    category = binarization.module.category
    all_jobs = Job.objects.filter(category__exact=category)
    all_names = [j.name for j in all_jobs]
    create_job_from_plugins(binarization.module.functions, all_names, category)
