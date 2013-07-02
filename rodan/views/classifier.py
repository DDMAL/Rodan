import os
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
    paginate_by = None

    def get_queryset(self):
        queryset = Classifier.objects.all()
        project = self.request.QUERY_PARAMS.get('project', None)

        if project:
            queryset = queryset.filter(project__uuid=project)

        return queryset

    @receiver(post_save, sender=Classifier)
    def create_xml(sender, instance=None, created=False, **kwargs):
        print 'create_xml'
        if created:
            instance._create_new_xml()

    def post(self, request, *args, **kwargs):
        print 'post'
        response = self.create(request, *args, **kwargs)  # Try using super
          # I think that (create) will actually call create_xml and therefore _create_new_xml
        if request.FILES:
            # # Making dirs should be done by 'save,' which is done in 'create'
            # if not os.path.exists(self.directory_path):
            #     os.makedirs(self.directory_path)

            # page_obj.page_image.save(page_obj.upload_path(fileobj.name), fileobj)
                # Hmmm, super does the django save... I haven't overwritten save on the classifier object...
                # maybe that's the best way?  The alternative I'm thinking of is to do it all here (in the view.)  That seems fine.
            # I believe that there's a better, Django-y way to do this... (call save and give the file as an argument, and set the path
            # variables properly)
            # f = open(self.object.file_path, 'w')
            # f.write(request.FILES['files'])

            # Write to filesystem (reference: https://docs.djangoproject.com/en/dev/topics/http/file-uploads/)
            uploaded_xml_file = request.FILES['files']
            with open(self.object.file_path, 'w') as destination:
                for chunk in uploaded_xml_file.chunks():
                    destination.write(chunk)
        return response


class ClassifierDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Classifier
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ClassifierSerializer

    def patch(self, request, pk, *args, **kwargs):
        kwargs['partial'] = True
        glyphs = request.DATA.get('glyphs', None)
        if glyphs:
            self.get_object().write_xml(glyphs)

        return self.update(request, *args, **kwargs)

    def delete(self, request, pk, *args, **kwargs):
        self.get_object().delete_xml()
        return self.destroy(request, *args, **kwargs)  # See class RetrieveUpdateDestroyAPIView
