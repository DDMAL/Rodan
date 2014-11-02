from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer


class InputPortTypeList(generics.ListAPIView):
    """
    Returns a list of InputPortTypes. Does not accept POST requests, since
    InputPortTypes should be defined and loaded server-side.
    """
    model = InputPortType
    serializer_class = InputPortTypeSerializer
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
#
#        return self.create(request, *args, **kwargs)


class InputPortTypeDetail(generics.RetrieveAPIView):
    """
    Query a single InputPortType instance.
    """
    model = InputPortType
    serializer_class = InputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
