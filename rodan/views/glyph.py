from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from rodan.models.classifier import Classifier
from rodan.models.pageglyphs import PageGlyphs
from rodan.models.glyph import Glyph
from rodan.helpers.json_response import JsonResponse


class GlyphDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    # serializer_class = GlyphSerializer  # May be easier to implement it all by hand

    def get(self, request, pk, *args, **kwargs):
        print "Glyph Get!"
        glyph_id = pk
        classifier_pk = request.DATA.get('classifier')
        pageglyphs_pk = request.DATA.get('pageglyphs')

        if classifier_pk is not None:
            gameraXML = Classifier.objects.get(pk=classifier_pk)
        elif pageglyphs_pk is not None:
            gameraXML = PageGlyphs.objects.get(pk=pageglyphs_pk)
        else:
            return Response({"message": "You must supply a url for a classifier or pageglyphs model that contains the glyph."}, status=status.HTTP_400_BAD_REQUEST)

        xml_file = gameraXML.file_path
        g = Glyph.from_file_with_id(xml_file, glyph_id)

        return JsonResponse(g.__dict__)  # Also try the glyph serializer.  (Try using super... although that wouldn't quite do it)

    def post(self, request, *args, **kwargs):
        print "Glyph Post!"
        classifier_pk = request.DATA.get('classifier')
        pageglyphs_pk = request.DATA.get('pageglyphs')

        if classifier_pk is None and pageglyphs_pk is None:
            return Response({"message": "You must supply a url for a classifier or pageglyphs model to which the glyph should be added."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            json_glyph = request.DATA.get('glyph')

            if classifier_pk is not None:
                classifier = Classifier.objects.get(pk=classifier_pk)
                xml_file = classifier.file_path
                Glyph.create(json_glyph, xml_file)

            if pageglyphs_pk is not None:
                pageglyphs = PageGlyphs.objects.get(pk=classifier_pk)
                xml_file = pageglyphs.file_path
                Glyph.create(json_glyph, xml_file)

            return super(GlyphDetail, self).post(self, request, *args, **kwargs)

    def patch(self, request, pk, *args, **kwargs):
        print "Glyph Patch!"
        glyph_id = pk
        classifier_pk = request.DATA.get('classifier')
        pageglyphs_pk = request.DATA.get('pageglyphs')

        if classifier_pk is None and pageglyphs_pk is None:
            return Response({"message": "You must supply a url for a classifier or pageglyphs model that contains the glyph."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if classifier_pk is not None:
                classifier = Classifier.objects.get(pk=classifier_pk)
                xml_file = classifier.file_path
                Glyph.update(request.DATA, xml_file, glyph_id)

            if pageglyphs_pk is not None:
                pageglyphs = PageGlyphs.objects.get(pk=classifier_pk)
                xml_file = pageglyphs.file_path
                Glyph.update(request.DATA, xml_file, glyph_id)

            # What do I return??
            # Not using Django, but maybe the Rest framework will do all the work for me
            # From what I know about theClassifier ensureSaved... I think Ratatosk expects the
            # new object back.  Maybe Rest will use my serializer
            return super(GlyphDetail, self).patch(self, request, pk, *args, **kwargs)

    def delete(self, request, pk, *args, **kwargs):
        # delete a glyph from a classifier and/or pageglyphs
        print "Glyph Delete!"
        glyph_id = pk
        classifier_pk = request.DATA.get('classifier')
        pageglyphs_pk = request.DATA.get('pageglyphs')

        if classifier_pk is None and pageglyphs_pk is None:
            return Response({"message": "You must supply a url for a classifier or pageglyphs model that contains the glyph."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if classifier_pk is not None:
                classifier = Classifier.objects.get(pk=classifier_pk)
                xml_file = classifier.file_path
                Glyph.destroy(xml_file, glyph_id)

            if pageglyphs_pk is not None:
                pageglyphs = PageGlyphs.objects.get(pk=classifier_pk)
                xml_file = pageglyphs.file_path
                Glyph.destroy(xml_file, glyph_id)

            return super(GlyphDetail, self).delete(self, request, pk, *args, **kwargs)
        return

