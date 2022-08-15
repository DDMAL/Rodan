import uuid
from django.db import models
from django.contrib.auth.models import User


class Tempauthtoken(models.Model):
    """
    A temporary token for users to authenticate in new tab. This has been made
    for viewing resources.

    **Fields**

    - `uuid`
    - `expiry`
    - `user` -- a foreign key to the `User` who wants a temporary token.
    """

    class Meta:
        app_label = "rodan"
        permissions = (("view_tempauthtoken", "View Temp Authtoken"),)

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    expiry = models.DateTimeField(null=True, db_index=True)
    user = models.OneToOneField(
        User, related_name="temp_authtoken", on_delete=models.CASCADE
    )

    def __str__(self):
        return "<TempAuthtoken {0} {1}>".format(str(self.uuid), self.user_id)
