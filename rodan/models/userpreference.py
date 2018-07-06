import uuid
from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
    """
    A `UserPreference` is associated with a 'User'.

    **Fields**

    - `uuid`
    - `user` -- assigned 'User' of this `UserPreference`.
    - `send_email` -- a field storing whether the User wants to receive emails.
    """

    class Meta:
        app_label = "rodan"
        permissions = (("view_userpreference", "View User Preference"),)

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.OneToOneField(
        User, related_name="user_preference", on_delete=models.CASCADE, db_index=True
    )
    send_email = models.BooleanField(default=True, db_index=True)

    def __unicode__(self):
        return u"<UserPreference {0}>".format(str(self.uuid))
