# from gamera.plugins import transformation
# from rodan.models.job import Job
# from rodan.jobs.gamera.helpers import create_job_from_plugins
# def load_module():
#     print "Loading transformation module"
#     category = transformation.module.category
#     all_jobs = Job.objects.filter(category__exact=category)
#     all_names = [j.name for j in all_jobs]
#     create_job_from_plugins(transformation.module.functions, all_names, category)
