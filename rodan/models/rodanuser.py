from django.db import models
from django.contrib.auth.models import User


class RodanUser(models.Model):
    class Meta:
        app_label = 'rodan'

    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.user.username


# Defines a post_save hook to ensure that a RodanUser is created for each User
def create_rodan_user(sender, instance, created, **kwargs):
    if created:
        RodanUser.objects.create(user=instance)
models.signals.post_save.connect(create_rodan_user, sender=User)
