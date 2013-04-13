import urlparse
from django.core.urlresolvers import resolve

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from rodan.models.workflow import Workflow
from rodan.models.page import Page
from rodan.serializers.workflow import WorkflowSerializer, WorkflowListSerializer


class WorkflowList(generics.ListCreateAPIView):
    model = Workflow
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = WorkflowListSerializer
    paginate_by = None


class WorkflowDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Workflow
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    permission_classes = (permissions.AllowAny, )
    serializer_class = WorkflowSerializer

    def patch(self, request, pk, *args, **kwargs):
        kwargs['partial'] = True
        print request.DATA
        workflow = Workflow.objects.get(pk=pk)
        if not workflow:
            return Response({'message': "Workflow not found"}, status=status.HTTP_404_NOT_FOUND)

        pages = request.DATA.get('pages', None)
        if pages:
            for page in pages:
                value = urlparse.urlparse(page['url']).path
                # resolve the URL we're passed to a page object
                try:
                    p = resolve(value)
                except:
                    return Response({'message': 'Could not resolve path to page object'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # check if the page already exists on this workflow. If so, we skip it.
                relationship_exists = workflow.pages.filter(pk=p.kwargs.get('pk')).exists()
                if relationship_exists:
                    continue

                # now use the pk to grab the Page object from the database
                page_obj = Page.objects.get(pk=p.kwargs.get('pk'))
                # finally, add this page to the workflow
                if not page_obj:
                    return Response({'message': 'Page Object was not found'}, status=status.HTTP_404_NOT_FOUND)

                workflow.pages.add(page_obj)
            del request.DATA['pages']

        return self.update(request, *args, **kwargs)
