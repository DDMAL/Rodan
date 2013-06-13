from rest_framework import generics
from rest_framework import permissions
from django.dispatch import receiver
from django.db.models.signals import post_save

from rodan.models.classifier import Classifier
from rodan.serializers.classifier import ClassifierSerializer, ClassifierListSerializer

#import ast


class ClassifierList(generics.ListCreateAPIView):
    model = Classifier
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ClassifierListSerializer

    def get_queryset(self):
        print "ClassifierList.get_queryset"
        queryset = Classifier.objects.all()
        project = self.request.QUERY_PARAMS.get('project', None)

        if project:
            queryset = queryset.filter(project__uuid=project)

        return queryset


@receiver(post_save, sender=Classifier)
def create_xml(sender, instance=None, created=False, **kwargs):
    print "create_xml"
    if created:
        instance.save()
        instance._create_new_xml()


class ClassifierDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Classifier
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ClassifierSerializer

    def patch(self, request, pk, *args, **kwargs):
        print "ClassifierDetail.patch"
        kwargs['partial'] = True
        glyphs = request.DATA.get('glyphs', None)
        if glyphs:
            self.get_object().write_xml(glyphs)

        return self.update(request, *args, **kwargs)

    def delete(self, request, pk, *args, **kwargs):
        print "ClassifierDetail.delete"
        self.get_object().delete_xml()
        return self.destroy(request, *args, **kwargs)  # See class RetrieveUpdateDestroyAPIView
