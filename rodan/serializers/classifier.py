from ClassifierInterface.models import Classifier
from rest_framework import serializers


class ClassifierSerializer(serializers.HyperlinkedModelSerializer):
    glyphs = serializers.Field(source="glyphs")

    class Meta:
        model = Classifier
        fields = ("url", "name", "glyphs")


class ClassifierListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Classifier
        fields = ("url", "name")

#class PngSerializer(serializers.HyperlinkedM
# Hmm... going simpler instead.  I don't really need a model nor a serializer right now.
