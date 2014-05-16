import celery
import urlparse
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from rodan.models.page import Page
from rodan.models.page import upload_path
from rodan.models.project import Project
from rodan.serializers.page import PageSerializer
from rodan.helpers.convert import ensure_compatible
from rodan.helpers.thumbnails import create_thumbnails
from rodan.helpers.processed import processed


class PageList(generics.ListCreateAPIView):
    model = Page
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = PageSerializer
    paginate_by = None

    def get_queryset(self):
        queryset = Page.objects.all()
        project = self.request.QUERY_PARAMS.get('project', None)

        if project:
            queryset = queryset.filter(project__uuid=project)

        return queryset

    # override the POST method to deal with multiple files in a single request
    def post(self, request, *args, **kwargs):
        if not request.FILES:
            return Response({'message': "You must supply at least one file to upload"}, status=status.HTTP_400_BAD_REQUEST)
        response = []
        current_user = User.objects.get(pk=request.user.id)

        start_seq = request.DATA.get('page_order', None)
        if not start_seq:
            return Response({'message': "The start sequence for the page ordering may not be empty."}, status=status.HTTP_400_BAD_REQUEST)

        project = request.DATA.get('project', None)
        if not project:
            return Response({"message": "You must supply a project identifier for the pages."}, status=status.HTTP_400_BAD_REQUEST)
        value = urlparse.urlparse(project).path

        try:
            p = resolve(value)
        except:
            return Response({"message": "Could not resolve {0} to a Project"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(pk=p.kwargs.get("pk"))
        except:
            return Response({"message": "You must specify an existing project for this page"}, status=status.HTTP_400_BAD_REQUEST)

        for seq, fileobj in enumerate(request.FILES.getlist('files'), start=int(start_seq)):
            page_obj = Page()
            page_obj.name = fileobj.name
            page_obj.project = project
            page_obj.page_order = seq
            page_obj.creator = current_user
            page_obj.save()
            page_obj.page_image.save(upload_path(page_obj, fileobj.name), fileobj)

            # Create a chain that will first ensure the
            # file is converted to PNG and then create the thumbnails.
            # The ensure_compatible() method returns the page_object
            # as the first (invisible) argument to the create_thumbnails
            # method.
            res = celery.chain(ensure_compatible.s(page_obj), create_thumbnails.s(), processed.s())
            res.apply_async()

            try:
                d = PageSerializer(page_obj).data
                response.append(d)
            except:
                return Response({"message": "Could not serialize page object"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"pages": response}, status=status.HTTP_201_CREATED)


class PageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Page
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = PageSerializer
