from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rodan.models.user import User


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None:
            email = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user.
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user