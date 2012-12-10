from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rodan.models.page import Page
from rodan.models.project import Project


@csrf_exempt  # REMOVE FOR PRODUCTION
@api_view(("POST",))
def page_upload(request):
    print request.POST
    resp = []
    for seq, afile in enumerate(request.FILES.getlist("files")):
        proj = Project.objects.get(pk=1)
        page = Page(project=proj, page_image=afile, page_order=seq)
        page.save()
    # for seq, uploaded_file in enumerate(files):
    #     print seq
        # print "Name: ", uploaded_file.name
        # print "Size: ", uploaded_file.size
    return Response({'success': True})
