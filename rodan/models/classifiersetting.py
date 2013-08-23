import os
from django.db import models
from django.conf import settings
from uuidfield import UUIDField


class ClassifierSetting(models.Model):
    """
        A model wrapper around the gamera classifier settings xml file.
        The xml file can be used in the classification jobs to provide
        feature weights.

        A setting file is typically produced from a classifier optimization
        task, in which case the setting will be linked to an `optimizationrun`
        record.
    """

    @property
    def setting_directory(self):
        return os.path.join(self.project.project_path, 'classifier_settings')

    def upload_fn(self, filename):
        _, ext = os.path.splitext(os.path.basename(filename))
        return os.path.join(self.setting_directory, "{0}{1}".format(str(self.uuid), ext))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    settings_file = models.FileField(upload_to=upload_fn, null=True, blank=True, max_length=512)
    project = models.ForeignKey("rodan.Project", related_name="classifier_settings")

    fitness = models.FloatField(null=True, blank=True)
    producer = models.ForeignKey('rodan.Classifier', related_name="classifier_settings", null=True, blank=True)

    creator = models.ForeignKey("auth.User", related_name="classifier_settings", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def file_url(self):
        if self.settings_file:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.settings_file.path, settings.MEDIA_ROOT))

    def __unicode__(self):
        return u"<ClassifierSetting {0}>".format(str(self.name))

    class Meta:
        app_label = 'rodan'

    def delete(self, *args, **kwargs):
        if os.path.exists(self.settings_file.path):
            os.remove(self.settings_file.path)
        super(ClassifierSetting, self).delete(*args, **kwargs)
