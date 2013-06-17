
from rodan.models.classifier import Classifier
from rest_framework import serializers


class ClassifierSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    glyphs = serializers.Field(source="glyphs")

    class Meta:
        model = Classifier
        fields = ("url", "project", "name", "glyphs")


class MinimalClassifierSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")

    class Meta:
        model = Classifier
        fields = ("url", "project", "name")
