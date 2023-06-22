from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.conf import settings
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class SendEmailResetSerializer(serializers.Serializer):
    """
    This serializer is used in place of `djoser.serializers.SendEmailResetSerializer` 
    to send activation and password reset emails via `username` instead of `email`.
    This is because `email` is not a unique field in the `User` model.
    """
    username = serializers.CharField(required=True)
    default_error_messages = {"user_not_found": settings.CONSTANTS.messages.USERNAME_NOT_FOUND}

    def get_user(self, is_active=True):
        try:
            user = User._default_manager.get(
                is_active=is_active, username=self.data.get("username", "")
            )
            if user.has_usable_password():
                return user

        except User.DoesNotExist:
            pass

        if (
            settings.PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND
            or settings.USERNAME_RESET_SHOW_EMAIL_NOT_FOUND
        ):
            self.fail("user_not_found")

