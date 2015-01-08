from rest_framework import serializers
import json

class AbsoluteURLField(serializers.Field):
    def to_representation(self, relative_url):
        """
        http://www.django-rest-framework.org/api-guide/fields/
        """
        if relative_url is not None:
            request = self.context['request']
            return request.build_absolute_uri(relative_url)
        else:
            return None

class TransparentField(serializers.Field):
    """
    Transparently pass the data through the serializer.

    Useful for JSONField, which takes care of serialization/deserialization under the hood.
    """
    def to_representation(self, data):
        return data
    def to_internal_value(self, data):
        return data
