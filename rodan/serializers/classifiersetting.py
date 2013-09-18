from rodan.models.classifiersetting import ClassifierSetting
from rest_framework import serializers


class ClassifierSettingSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.Field(source="uuid")
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
                  'optimization_started_at',
                  'optimization_finished_at',
                  "creator",
                  "created",
                  "updated")
