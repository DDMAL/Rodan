from rodan.models import UserPreference
from rest_framework import serializers


class UserPreferenceSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field="id", lookup_url_kwarg="pk")

    class Meta:
        model = UserPreference
        fields = ('url',
                  'user',
                  'send_email')


class UserPreferenceListSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field="id", lookup_url_kwarg="pk")

    class Meta:
        model = UserPreference
        fields = ('url',
                  'user',
                  'send_email')