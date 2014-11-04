from django import template
from rest_framework.views import get_view_description
register = template.Library()

@register.filter(name='to_html')
def to_html(docstring):
    class A: pass   # manage to use REST framework code.
    A.__doc__ = docstring
    return get_view_description(A, html=True)

@register.filter(name='getattr')
def _getattr(d, k):
    return getattr(d, k)
