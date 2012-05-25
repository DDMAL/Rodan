# Create your views here.
from django.shortcuts import render
from projects.models import Page,Workflow
from processing.models import Result,Binarize


def simple_binarize_view(request,page_id):
    page = Page.objects.get(pk=page_id)
    data = {
        'page':page
    }

    if request.method == 'POST' :
        thresh_value = request.POST['thresh_value']
        wf = Workflow(name="someworkflow",description="only binarize workflow",project=page.project)
        wf.save()
        res = Result.objects.create(work_flow=wf, page=page)
        res.save()
        bin = Binarize.objects.create(threshold_value=int(thresh_value), result=res)
        binarized_img_loc = bin.binarize_image()
        #make some template to display the img?

    return render(request, 'processing/binarize.html', data)