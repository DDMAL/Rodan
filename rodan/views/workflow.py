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
    # permission_classes = (permissions.IsAuthenticated, )
    permission_classes = (permissions.AllowAny, )
    serializer_class = WorkflowListSerializer
    paginate_by = None

    def get_queryset(self):
        queryset = Workflow.objects.all()
        project = self.request.QUERY_PARAMS.get('project', None)

        if project:
            queryset = queryset.filter(project__uuid=project)

        return queryset


class WorkflowDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Workflow
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowSerializer

    def patch(self, request, pk, *args, **kwargs):
        kwargs['partial'] = True
        workflow = Workflow.objects.get(pk=pk)
        if not workflow:
            return Response({'message': "Workflow not found"}, status=status.HTTP_404_NOT_FOUND)

        pages = request.DATA.get('pages', None)
        if pages is not None:  # Remember pages can be empty array.
            workflow_pages = []

            for page in pages:
                value = urlparse.urlparse(page['url']).path

                # resolve the URL we're passed to a page object
                try:
                    p = resolve(value)
                except:
                    return Response({'message': 'Could not resolve path to page object'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                page_obj = Page.objects.get(pk=p.kwargs.get('pk'))
                if not page_obj:
                    return Response({'message': 'Page Object was not found'}, status=status.HTTP_404_NOT_FOUND)

                workflow_pages.append(page_obj)

            workflow.pages = workflow_pages
            workflow.save()

            del request.DATA['pages']

        return self.update(request, *args, **kwargs)
