from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from rodan.models.page import Page
from rodan.serializers.page import PageSerializer
from rodan.helpers.convert import ensure_compatible
from rodan.helpers.thumbnails import create_thumbnails
from rodan.helpers.pagedone import pagedone


class PageList(generics.ListCreateAPIView):
    model = Page
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = PageSerializer

    # override the POST method to deal with multiple files in a single request
    def post(self, request, *args, **kwargs):
        if not request.FILES:
            return Response({'error': "You must supply at least one file to upload"}, status=status.HTTP_400_BAD_REQUEST)
        response = []
        current_user = User.objects.get(pk=request.user.id)

        start_seq = int(request.POST['page_order'])

        for seq, fileobj in enumerate(request.FILES.getlist('files'), start=start_seq):
            data = {
                'name': fileobj.name,
                'project': request.POST['project'],
                'page_order': seq,
            }

            pagefile = {
                'page_image': fileobj
            }
            serializer = PageSerializer(data=data, files=pagefile)

            if serializer.is_valid():
                page_object = serializer.save()

                page_object.creator = current_user
                page_object.save()

                # Create a chain that will first ensure the
                # file is converted to PNG and then create the thumbnails.
                # The ensure_compatible() method returns the page_object
                # as the first (invisible) argument to the create_thumbnails
                # method.
                res = ensure_compatible.s(page_object)
                res.link(create_thumbnails.s())
                res.link(pagedone.s())
                res.apply_async()

                response.append(serializer.data)
            else:
                # if there's an error, bail early and send the error back to the client
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'pages': response}, status=status.HTTP_201_CREATED)


class PageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Page
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = PageSerializer
