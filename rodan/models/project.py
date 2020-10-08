import os
import logging
import shutil
import uuid
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.db import models


logger = logging.getLogger("rodan")

class Project(models.Model):
    """
    The top-level model. A `Project` is mostly administrative and organizational.
    `Resource`s, `Workflow`s belong to `Project`s.

    **Fields**

    - `uuid`
    - `name`
    - `description`
    - `creator` -- a foreign key to the `User` who created the `Project`. Considered
      as the superuser of the `Project`.
    - `created`
    - `updated`

    **Properties**

    - `project_path` -- the project directory in the filesystem.
    - `workflow_count` -- the count of `Workflow`s under the `Project`.
    - `resource_count` --  the count of `Resource`s under the `Project`.

    **Methods**

    - `save` -- create the project directory if it does not exist.
    - `delete` -- delete the whole project directory.
    """

    class Meta:
        app_label = "rodan"
        permissions = (("view_project", "View Project"),)

    @property
    def project_path(self):
        return os.path.join(
            settings.MEDIA_ROOT, "projects", self.uuid.hex
        )  # backward compatible (not using hyphenated UUID)

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True, db_index=True)
    creator = models.ForeignKey(
        User, related_name="projects", on_delete=models.PROTECT, db_index=True
    )

    admin_group = models.ForeignKey(Group, related_name="project_as_admin")
    worker_group = models.ForeignKey(Group, related_name="project_as_worker")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __unicode__(self):
        return u"<Project {0}>".format(self.name)

    def ensure_groups(self, save=True):
        try:
            self.admin_group
            if self.admin_group is None:
                raise Group.DoesNotExist("Group not exist")
        except Group.DoesNotExist:
            self.admin_group = Group.objects.create(
                name="project/{0}/admin".format(self.pk)
            )
        try:
            self.worker_group
            if self.worker_group is None:
                raise Group.DoesNotExist("Worker not exist")
        except Group.DoesNotExist:
            self.worker_group = Group.objects.create(
                name="project/{0}/worker".format(self.pk)
            )

        if save:
            self.save(update_fields=["admin_group", "worker_group"])

    def save(self, *args, **kwargs):
        self.ensure_groups(save=False)
        super(Project, self).save(*args, **kwargs)
        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)

    def delete(self, *args, **kwargs):
        # remove protected links from input/output to resource by deleting all
        # workflowruns prior to resources
        from rodan.models import WorkflowRun

        WorkflowRun.objects.filter(project=self).delete()

        # delete project, project folder, and project groups
        proj_path = self.project_path
        ag = self.admin_group
        wg = self.worker_group
        super(Project, self).delete(*args, **kwargs)  # cascade deletion of resources
        ag.delete()
        wg.delete()
        logger.info("Deleting: {}".format(proj_path))
        try:
            shutil.rmtree(proj_path)
        except:
            logger.warning("Deleting folder failed: {}".format(proj_path))

    @property
    def workflow_count(self):
        return self.workflows.count()

    @property
    def resource_count(self):
        return self.resources.count()

    @property
    def resourcelist_count(self):
        return self.resourcelists.count()

    @property
    def admins_relurl(self):
        return reverse("project-detail-admins", args=(self.pk,))

    @property
    def workers_relurl(self):
        return reverse("project-detail-workers", args=(self.pk,))
