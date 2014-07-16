from rest_framework import generics
from rodan.models.output import Output
from rodan.serializers.output import OutputSerializer, OutputListSerializer


class OutputList(generics.ListCreateAPIView):
    model = Output
    paginate_by = None
    serializer_class = OutputListSerializer

    def get_queryset(self):
        return Output.objects.all()


class OutputDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Output
    serializer_class = OutputSerializer
