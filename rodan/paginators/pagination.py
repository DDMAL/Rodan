from rest_framework.pagination import BasePaginationSerializer, NextPageField, PreviousPageField
from rest_framework import serializers
from rest_framework.templatetags.rest_framework import replace_query_param

class PaginationSerializer(BasePaginationSerializer):
    """
    A default implementation of a pagination serializer.
    """
    count = serializers.ReadOnlyField(source='paginator.count')
    next = NextPageField(source='*')
    previous = PreviousPageField(source='*')
    current_page = serializers.ReadOnlyField(source="number")
    total_pages = serializers.ReadOnlyField(source="paginator.num_pages")
