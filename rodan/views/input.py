from rest_framework import generics
from rest_framework import permissions
from rodan.models.input import Input
from rodan.serializers.input import InputSerializer


class InputList(generics.ListCreateAPIView):
    model = Input
    paginate_by = None
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return Input.objects.all()


class InputDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Input
    serializer_class = InputSerializer
    permission_classes = (permissions.IsAuthenticated, )
