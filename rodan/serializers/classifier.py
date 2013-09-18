
from rodan.models.classifier import Classifier
from rest_framework import serializers
from rodan.serializers.pageglyphs import MinimalPageGlyphsSerializer


class ClassifierSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.Field(source="uuid")
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    file_path = serializers.Field(source="file_path")
    pageglyphs = MinimalPageGlyphsSerializer(many=True, required=False, read_only=True)
    glyphs = serializers.Field(source="glyphs")

    class Meta:
        model = Classifier
        fields = ("uuid", "url", "project", "name", "file_path", "optimal_setting", "pageglyphs", "glyphs")


class ClassifierListSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    pageglyphs = MinimalPageGlyphsSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Classifier
        fields = ("url", "project", "name", "optimal_setting", "pageglyphs")


class MinimalClassifierSerializer(serializers.HyperlinkedModelSerializer):
    pageglyphs = MinimalPageGlyphsSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Classifier
        fields = ("url", "name", "pageglyphs")
