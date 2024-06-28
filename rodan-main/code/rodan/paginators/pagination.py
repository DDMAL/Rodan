from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

class SafePaginator(Paginator):
    """
    A paginator that returns a valid page even if the page argument isn't a number or isn't 
    in range instead of throwing an exception.
    """
    def page(self, number):
        """
        Return a valid page, even if the page argument isn't a number or isn't
        in range.
        """
        try:
            number = self.validate_number(number)
        except PageNotAnInteger:
            number = 1
        except EmptyPage:
            number = self.num_pages
        
        return super(SafePaginator, self).page(number)


class CustomPagination(PageNumberPagination):
    """
        This pagination serializer adds the 'current_page' and 'total_pages' properties
        to the default Django Rest Framework pagination serializer.
    """

    page_size_query_param = "page_size"
    max_page_size = settings.REST_FRAMEWORK["MAX_PAGE_SIZE"]
    django_paginator_class = SafePaginator

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("current_page", self.page.number),
                    ("total_pages", self.page.paginator.num_pages),
                    ("results", data),
                ]
            )
        )


class CustomPaginationWithDisablePaginationOption(CustomPagination):
    """
    Add "disable_pagination" GET parameter on top of CustomPagination.
    """

    def get_paginated_response(self, data):
        if self.request.query_params.get("disable_pagination"):
            return Response(data)
        else:
            return super(
                CustomPaginationWithDisablePaginationOption, self
            ).get_paginated_response(data)

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get("disable_pagination"):
            self.request = request
            return queryset
        else:
            return super(
                CustomPaginationWithDisablePaginationOption, self
            ).paginate_queryset(queryset, request, view)
