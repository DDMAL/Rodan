import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Project(models.Model):
    class Meta:
        app_label = 'rodan'

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User)
    pk_name = 'project_id'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.projects.view', [str(self.id)])

    # Takes in a User (not a RodanUser), returns true if the user created it
    def is_owned_by(self, user):
        return user.is_authenticated() and self.creator == user.get_profile()

    def get_percent_done(self):
        percent_done = sum(page.get_percent_done() for page in self.page_set.all())
        return percent_done / self.page_set.count() if self.page_set.count() else 0

    def get_divaserve_dir(self):
        return os.path.join(settings.MEDIA_ROOT,
                            "%d" % self.id,
                            'final')

    def is_partially_complete(self):
        Job = models.get_model('rodan', 'Job')
        diva_job = Job.objects.get(pk='diva-preprocess')
        return any(page.get_percent_done() == 100 and page.workflow.jobitem_set.filter(job=diva_job).count() for page in self.page_set.all())

    def clone_workflow_for_page(self, workflow, page, user):
        Workflow = models.get_model('rodan', 'Workflow')
        new_wf = Workflow.objects.create(project=self, name=workflow.name, description=workflow.description, has_started=True)

        for jobitem in workflow.jobitem_set.all():
            new_wf.jobitem_set.create(sequence=jobitem.sequence, job=jobitem.job)

        page.workflow = new_wf
        page.save()

        return new_wf
