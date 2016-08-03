import uuid
from django.db import models
from django.contrib.auth.models import User


class Tempauthtoken(models.Model):

    class Meta:
        app_label = 'rodan'
        permissions = (
            ('view_tempauthtoken', 'View Temp Authtoken'),
        )

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    expiry = models.DateTimeField(null=True, db_index=True)
    user = models.ForeignKey(User, related_name="temp_authtoken", on_delete=models.CASCADE, unique=True)

    def __unicode__(self):
        return u"<TempAuthtoken {0} {1}>".format(str(self.uuid), self.user_id)
