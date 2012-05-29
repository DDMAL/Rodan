# Create your views here.
from django.shortcuts import render
from projects.models import Page,Workflow
from processing.models import Result

from processing.core import binarise


def simple_binarise_view(request,page_id):
    page = Page.objects.get(pk=page_id)
    data = {
        'page':page
    }

    if request.method == 'POST' :
        thresh_value = request.POST['thresh_value']
        binarised_img_loc = binarise.simple_binarise_image(page,int(thresh_value))
        #result = Result.objects.create(job=)

    return render(request, 'processing/binarise.html', data)