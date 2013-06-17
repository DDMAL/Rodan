from rest_framework import generics
from rest_framework import permissions
from django.dispatch import receiver
from django.db.models.signals import post_save

from rodan.models.pageglyphs import PageGlyphs
from rodan.serializers.pageglyphs import PageGlyphsSerializer, PageGlyphsListSerializer

#import ast


class PageGlyphsList(generics.ListCreateAPIView):
    model = PageGlyphs
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = PageGlyphsListSerializer
    paginate_by = None

    @receiver(post_save, sender=PageGlyphs)
    def create_xml(sender, instance=None, created=False, **kwargs):
        if created:
            instance._create_new_xml()


class PageGlyphsDetail(generics.RetrieveUpdateDestroyAPIView):
    model = PageGlyphs
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = PageGlyphsSerializer

    def patch(self, request, pk, *args, **kwargs):
        kwargs['partial'] = True
        glyphs = request.DATA.get('glyphs', None)
        if glyphs:
            self.get_object().write_xml(glyphs)

        return self.update(request, *args, **kwargs)

    def delete(self, request, pk, *args, **kwargs):
        self.get_object().delete_xml()
        return self.destroy(request, *args, **kwargs)  # See class RetrieveUpdateDestroyAPIView
