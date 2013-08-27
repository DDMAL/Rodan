from rest_framework import generics, permissions
from rodan.models.classifier import Classifier
from rodan.models.classifiersetting import ClassifierSetting
from rodan.serializers.classifiersetting import ClassifierSettingSerializer
from rodan.helpers.dbmanagement import resolve_object_from_url

class ClassifierSettingList(generics.ListCreateAPIView):
    model = ClassifierSetting
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ClassifierSettingSerializer
    paginate_by = None

    def get_queryset(self):
        queryset = ClassifierSetting.objects.all()
        project = self.request.QUERY_PARAMS.get('project', None)

        if project:
            queryset = queryset.filter(project__uuid=project)

        producer_url = self.request.QUERY_PARAMS.get('producer', None)
        if producer_url:
            try:
                classifier_instance = resolve_object_from_url(Classifier, producer_url)
            except Classifier.DoesNotExist:
                return queryset

            queryset = queryset.filter(producer=classifier_instance)

        return queryset

    def post(self, request, *args, **kwargs):
        response = super(ClassifierSetting, self).post(request, *args, **kwargs)

        if request.FILES:
            uploaded_xml_file = request.FILES['files']

            with open(self.object.settings_file.path, 'w') as destination:
                for chunk in uploaded_xml_file.chunks():
                    destination.write(chunk)

        return response

class ClassifierSettingDetail(generics.RetrieveUpdateDestroyAPIView):
    model = ClassifierSetting
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ClassifierSettingSerializer
    paginate_by = None
