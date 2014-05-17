
from rodan.models.pageglyphs import PageGlyphs
from rest_framework import serializers


class PageGlyphsSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.Field(source="uuid")
    file_path = serializers.Field(source="file_path")
    glyphs = serializers.Field(source="glyphs")

    class Meta:
        model = PageGlyphs
        fields = ("uuid", "url", "classifier", "file_path", "glyphs")


class PageGlyphsListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PageGlyphs
        fields = ("url", "classifier")


class MinimalPageGlyphsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PageGlyphs
        fields = ("url",)
