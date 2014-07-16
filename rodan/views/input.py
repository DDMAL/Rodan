from rest_framework import generics
from rodan.models.input import Input
from rodan.serializers.input import InputSerializer


class InputList(generics.ListCreateAPIView):
    model = Input
    paginate_by = None

    def get_queryset(self):
        return Input.objects.all()


class InputDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Input
    serializer_class = InputSerializer
