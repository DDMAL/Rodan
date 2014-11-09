from rest_framework import generics
from rest_framework import permissions
from rodan.models.outputporttype import OutputPortType
from rodan.serializers.outputporttype import OutputPortTypeSerializer


class OutputPortTypeList(generics.ListAPIView):
    """
    Returns a list of OutputPortTypes. Does not accept POST requests, since
    OutputPortTypes should be defined and loaded server-side.
    """
    model = OutputPortType
    serializer_class = OutputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )

#    def post(self, request, *args, **kwargs):
#        job = request.DATA.get('job', None)
#
#        try:
#            resolve_to_object(job, Job)
#        except AttributeError:
#            return Response({'message': "Please specify a job"}, status=status.HTTP_400_BAD_REQUEST)
#        except Job.DoesNotExist:
#            return Response({'message': "No job with the specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)
#        except Resolver404 as e:
#            return Response({'message': "Error resolving job object. {0}".format(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#        return self.create(request, *args, **kwargs)


class OutputPortTypeDetail(generics.RetrieveAPIView):
    """
    Query a single OutputPortType instance.
    """
    model = OutputPortType
    serializer_class = OutputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
