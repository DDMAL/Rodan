# Create your views here.
from django.shortcuts import render
from projects.models import Page,Workflow
from processing.models import Result,Binarise


def simple_binarise_view(request,page_id):
    page = Page.objects.get(pk=page_id)
    data = {
        'page':page
    }

    if request.method == 'POST' :
        thresh_value = request.POST['thresh_value']
        wf = Workflow(name="someworkflow",description="only binarise workflow",project=page.project)
        wf.save()
        res = Result.objects.create(work_flow=wf, page=page)
        res.save()
        bin = Binarise.objects.create(threshold_value=int(thresh_value), result=res)
        binarised_img_loc = bin.binarise_image()
        #make some template to display the img?

    return render(request, 'processing/binarise.html', data)