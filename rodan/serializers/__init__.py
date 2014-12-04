from rest_framework import serializers

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
