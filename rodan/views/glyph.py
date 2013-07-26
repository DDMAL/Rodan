from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from rodan.models.classifier import Classifier
from rodan.models.pageglyphs import PageGlyphs
from rodan.models.glyph import Glyph
from rodan.helpers.json_response import JsonResponse
from rodan.jobs.util.taskutil import get_uuid_from_url  # TODO: perhaps this should be moved into helpers.


class GlyphDetail(generics.RetrieveUpdateDestroyAPIView):
    # model = Glyph
    permission_classes = (permissions.IsAuthenticated, )
    # serializer_class = GlyphSerializer  # May be easier to implement it all by hand

    def get(self, request, pk, *args, **kwargs):
        print "Glyph Get!"
        glyph_id = pk
        classifier_url = request.DATA.get('classifier_url')
        pageglyphs_url = request.DATA.get('pageglyphs_url')

        if classifier_url is not None:
            classifier_pk = get_uuid_from_url(classifier_url)
            gameraXML = Classifier.objects.get(pk=classifier_pk)
        elif pageglyphs_url is not None:
            pageglyphs_pk = get_uuid_from_url(pageglyphs_url)
            gameraXML = PageGlyphs.objects.get(pk=pageglyphs_pk)
        else:
            return Response({"message": "You must supply a url for a classifier or pageglyphs model that contains the glyph."}, status=status.HTTP_400_BAD_REQUEST)

        xml_file = gameraXML.file_path
        g = Glyph.from_file_with_id(xml_file, glyph_id)

        return JsonResponse(g.__dict__)  # Also try the glyph serializer.  (Try using super... although that wouldn't quite do it)
                                         # maybe I can manually call the serializer on with g.

    def post(self, request, *args, **kwargs):
        print "Glyph Post!"
        classifier_url = request.DATA.get('classifier_url')

        if classifier_url is None:
            return Response({"message": "You must supply a url for a classifier to which the glyph should be added."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            classifier_pk = get_uuid_from_url(classifier_url)
            classifier = Classifier.objects.get(pk=classifier_pk)
            xml_file = classifier.file_path
            json_glyph = request.DATA.get('glyph')
            g = Glyph.create(json_glyph, xml_file)

        return JsonResponse(g.__dict__)

    def patch(self, request, pk, *args, **kwargs):
        print "Glyph Patch!"
        glyph_id = pk
        classifier_url = request.DATA.get('classifier_url')
        pageglyphs_url = request.DATA.get('pageglyphs_url')
        # print "glyph_id: " + glyph_id
        # print "classifier_url: " + classifier_url
        # print "pageglyphs_url: " + pageglyphs_url

        if classifier_url is None and pageglyphs_url is None:
            return Response({"message": "You must supply a url for a classifier or pageglyphs model that contains the glyph."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if classifier_url is not None:
                classifier_pk = get_uuid_from_url(classifier_url)
                classifier = Classifier.objects.get(pk=classifier_pk)
                xml_file = classifier.file_path
                g = Glyph.update(request.DATA, xml_file, glyph_id)

            if pageglyphs_url is not None:
                pageglyphs_pk = get_uuid_from_url(pageglyphs_url)
                pageglyphs = PageGlyphs.objects.get(pk=pageglyphs_pk)
                xml_file = pageglyphs.file_path
                g = Glyph.update(request.DATA, xml_file, glyph_id)

            return JsonResponse(g.__dict__)

    def delete(self, request, pk, *args, **kwargs):
        # delete a glyph from a classifier and/or pageglyphs
        print "Glyph Delete!"
        glyph_id = pk
        classifier_url = request.DATA.get('classifier_url')
        pageglyphs_url = request.DATA.get('pageglyphs_url')

        if classifier_url is None and pageglyphs_url is None:
            return Response({"message": "You must supply a url for a classifier or pageglyphs model that contains the glyph."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if classifier_url is not None:
                classifier_pk = get_uuid_from_url(classifier_url)
                classifier = Classifier.objects.get(pk=classifier_pk)
                xml_file = classifier.file_path
                g = Glyph.destroy(xml_file, glyph_id)

            if pageglyphs_url is not None:
                pageglyphs_pk = get_uuid_from_url(pageglyphs_url)
                pageglyphs = PageGlyphs.objects.get(pk=pageglyphs_pk)
                xml_file = pageglyphs.file_path
                g = Glyph.destroy(xml_file, glyph_id)

            return JsonResponse(g.__dict__)
