from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models.job import Job
from rodan.models.outputporttype import OutputPortType
from rodan.serializers.outputporttype import OutputPortTypeSerializer


class OutputPortTypeList(generics.ListCreateAPIView):
    model = OutputPortType
    serializer_class = OutputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None

    def post(self, request, *args, **kwargs):
        minimum = request.DATA.get('minimum', None)
        maximum = request.DATA.get('maximum', None)
        resource_type = request.DATA.get('resource_type', None)

        if not minimum or not maximum:
            return Response({"message": "You must specify minimum and maximum for this OutputPortType"}, status=status.HTTP_400_BAD_REQUEST)

        job = request.DATA.get('job', None)

        try:
            job_obj = resolve_to_object(job, Job)
        except AttributeError:
            return Response({'message': "Please specify a job"}, status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
            return Response({'message': "No job with the specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)
        except Resolver404 as e:
            return Response({'message': "Error resolving job object. {0}".format(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        OutputPortType(job=job_obj,
                       resource_type=resource_type,
                       minimum=minimum,
                       maximum=maximum).save()

        return Response(status=status.HTTP_201_CREATED)


class OutputPortTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    model = OutputPortType
    serializer_class = OutputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
