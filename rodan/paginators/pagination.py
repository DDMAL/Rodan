from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.compat import OrderedDict

class CustomPagination(PageNumberPagination):
    """
        This pagination serializer adds the 'current_page' and 'total_pages' properties
        to the default Django Rest Framework pagination serializer.
    """
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))
