# Create your views here.
from django.shortcuts import render
from projects.models import Page,Workflow,Job
from processing.models import *

from processing.core import binarise


def simple_binarise_view(request,page_id):
    page = Page.objects.get(pk=page_id)
    data = {
        'page':page
    }

    if request.method == 'POST' :
        thresh_value = request.POST['thresh_value']
        binarised_img_loc = binarise.simple_binarise_image(page,int(thresh_value))

        #the following job instance is just a dummy job, to assist in creation of a result
        job = Job.objects.create(name="dat bin job",description="i <3 bin",module="BI")
        result = Result.objects.create(job=job,page=page,rodan_user=request.user.get_profile())
        ActionParameter.objects.create(key="threshold_value", value=thresh_value,result=result)

        path,filename = os.path.split(binarised_img_loc)

        ResultFile.objects.create(file_name=filename,path_to_file=path,result=result)
        #render a page to display the result?

    return render(request, 'processing/binarise.html', data)