from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    projects = serializers.ManyHyperlinkedRelatedField(view_name='project-detail')

    class Meta:
        model = User
        fields = ('url',
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    'is_staff',
                    'is_active',
                    'is_superuser',
                    'groups',
                    'projects')
