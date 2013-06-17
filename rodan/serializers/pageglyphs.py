
from rodan.models.pageglyphs import PageGlyphs
from rest_framework import serializers
from rodan.serializers.classifier import MinimalClassifierSerializer


class PageGlyphsSerializer(serializers.HyperlinkedModelSerializer):
    classifier = MinimalClassifierSerializer()
    glyphs = serializers.Field(source="glyphs")

    class Meta:
        model = PageGlyphs
        fields = ("url", "classifier", "name", "glyphs")


class PageGlyphsListSerializer(serializers.HyperlinkedModelSerializer):
    classifier = MinimalClassifierSerializer()

    class Meta:
        model = PageGlyphs
        fields = ("url", "classifier", "name")
