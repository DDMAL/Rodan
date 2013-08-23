from rodan.models.classifiersetting import ClassifierSetting
from rest_framework import serializers


class ClassifierSettingSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.Field(source="file_url")

    class Meta:
        model = ClassifierSetting
        read_only_fields = ('created',)
        fields = ("uuid",
                  "name",
                  "file_url",
                  'project',
                  'producer',
                  "fitness",
                  "creator",
                  "created",
                  "updated")
