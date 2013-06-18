
from rodan.models.pageglyphs import PageGlyphs
from rest_framework import serializers
#from rodan.serializers.classifier import MinimalClassifierSerializer


class PageGlyphsSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.Field(source="uuid")
    file_path = serializers.Field(source="file_path")
    glyphs = serializers.Field(source="glyphs")

    class Meta:
        model = PageGlyphs
        fields = ("uuid", "url", "classifier", "name", "file_path", "glyphs")


class PageGlyphsListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PageGlyphs
        fields = ("url", "classifier", "name")


class MinimalPageGlyphsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PageGlyphs
        fields = ("url", "name")
