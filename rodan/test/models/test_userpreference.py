from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models import UserPreference
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class UserPreferenceTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_user = mommy.make(User)
        self.test_project = mommy.make("rodan.Project")

        self.test_user_preference_data = {"user": self.test_user, "send_email": False}

    def test_delete(self):
        userpreference = UserPreference(**self.test_user_preference_data)
        userpreference.save()

        retr_userpreference = UserPreference.objects.get(user_id=self.test_user.id)
        retr_userpreference.delete()

        retr_userpreference = UserPreference.objects.filter(user_id=self.test_user.id)
        self.assertFalse(retr_userpreference.exists())
