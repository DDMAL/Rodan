# from django.db.models.signals import post_syncdb
# from rodan.models.job import Job
# from rodan.jobs import jobs

# """A post-syncdb hook to ensure that a row for every job defined under
# rodan/jobs is present in the jobs table.
# """


# def create_jobs(sender, **kwargs):
#     for module, job in jobs.iteritems():
#         if Job.objects.filter(module=module).count() == 0:
#             # This job does not exist in the database, so create it
#             Job.objects.create(module=module, slug=job.get_slug(), name=job.get_name(), enabled=job.enabled, is_automatic=job.is_automatic, is_required=job.is_required)

# post_syncdb.connect(create_jobs)
