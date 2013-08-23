from rest_framework import generics, permissions
from rodan.models.classifiersetting import ClassifierSetting
from rodan.serializers.classifiersetting import ClassifierSettingSerializer

class ClassifierSettingList(generics.ListCreateAPIView):
    model = ClassifierSetting
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ClassifierSettingSerializer
    paginate_by = None

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
