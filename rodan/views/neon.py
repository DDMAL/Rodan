from django.shortcuts import get_object_or_404
from rodan.utils import render_to_json
from rodan.models.projects import Page, Job
from rodan.jobs.neon_resources.modifymei import ModifyDocument

import json

j = Job.objects.get(pk='neon')

@render_to_json()
def insert_neume(request, page_id):
    if request.method == 'POST':
        before_id = str(request.POST.get('beforeid'))
        pname = str(request.POST.get('pname'))
        oct = str(request.POST.get('oct'))
        dot_form = request.POST.get('dotform')

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')
        
        md = ModifyDocument(fname)
        result = md.insert_punctum(before_id, pname, oct, dot_form, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_neume(request, page_id):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])

        id = str(data.get("id"))
        before_id = str(data.get("beforeid"))
        
        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        pitch_info = data.get("pitchInfo")

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.move_neume(id, before_id, pitch_info, ulx, uly, lrx, lry)
        md.write_doc()

        return {}

@render_to_json()
def delete_neume(request, page_id):
    if request.method == 'POST':
        ids = str(request.POST.get('ids'))

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.delete_neume(ids.split(","))
        md.write_doc()

        return {}

@render_to_json()
def update_neume_head_shape(request, page_id):
    if request.method == 'POST':
        id = str(request.POST.get('id'))
        head_shape = str(request.POST.get('shape'))
        
        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.update_neume_head_shape(id, head_shape, ulx, uly, lrx, lry)
        md.write_doc()

        return {}

@render_to_json()
def neumify(request, page_id):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        nids = str(data.get("nids")).split(",")
        type_id = str(data.get("typeid"))
        head_shapes = data.get("headShapes")

        try:
            lrx = str(data["lrx"])
            lry = str(data["lry"])
            ulx = str(data["ulx"])
            uly = str(data["uly"])
        except KeyError:
            ulx = uly = lrx = lry = None
        
        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        result = md.neumify(nids, type_id, head_shapes, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def ungroup(request, page_id):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])

        nids = str(data.get("nids"))
        bboxes = data.get("bbs")

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        result = md.ungroup(nids.split(','), bboxes)
        md.write_doc()

        return result

@render_to_json()
def insert_division(request, page_id):
    if request.method == 'POST':
        div_type = str(request.POST.get('type'))
        before_id = str(request.POST.get('beforeid'))

        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        result = md.insert_division(before_id, div_type, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_division(request, page_id):
    if request.method == 'POST':
        id = str(request.POST.get('id'))
        before_id = str(request.POST.get('beforeid'))

        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.move_division(id, before_id, ulx, uly, lrx, lry)
        md.write_doc()

        return {}

@render_to_json()
def delete_division(request, page_id):
    if request.method == 'POST':
        ids = str(request.POST.get('ids'))

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.delete_division(ids.split(","))
        md.write_doc()

        return {}

@render_to_json()
def insert_dot(request, page_id):
    if request.method == 'POST':
        id = str(request.POST.get('id'))
        dot_form = str(request.POST.get('dotform'))

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.add_dot(id, dot_form, ulx, uly, lrx, lry)
        md.write_doc()

        return {}

@render_to_json()
def delete_dot(request, page_id):
    if request.method == 'POST':
        id = str(request.POST.get('id'))

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.delete_dot(id, ulx, uly, lrx, lry)
        md.write_doc()

        return {}

@render_to_json()
def insert_clef(request, page_id):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        shape = str(data.get("shape")).upper()
        line = str(data.get("line"))
        before_id = str(data.get("beforeid"))

        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        result = md.insert_clef(line, shape, data["pitchInfo"], before_id, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_clef(request, page_id):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        clef_id = str(data.get("id"))
        
        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        line = str(data.get("line"))

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.move_clef(clef_id, line, data["pitchInfo"], ulx, uly, lrx, lry)
        md.write_doc()

        return {}

@render_to_json()
def update_clef_shape(request, page_id):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        clef_id = str(data.get("id"))

        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        shape = str(data.get("shape"))

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')
        
        md = ModifyDocument(fname)
        md.update_clef_shape(clef_id, shape, data["pitchInfo"], ulx, uly, lrx, lry)
        md.write_doc()

        return {}

@render_to_json()
def delete_clef(request, page_id):
    if request.method == 'POST':
        clefs_to_delete = json.loads(request.POST['data'])

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.delete_clef(clefs_to_delete)
        md.write_doc()

        return {}

@render_to_json()
def insert_custos(request, page_id):
    if request.method == 'POST':
        pname = str(request.POST.get('pname'))
        oct = str(request.POST.get('oct'))
        before_id = str(request.POST.get('beforeid'))

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None


        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        result = md.insert_custos(pname, oct, before_id, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_custos(request, page_id):
    if request.method == 'POST':
        custos_id = str(request.POST.get('id'))
        pname = str(request.POST.get('pname'))
        oct = str(request.POST.get('oct'))

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.move_custos(custos_id, pname, oct, ulx, uly, lrx, lry)
        md.write_doc()

        return {}

@render_to_json()
def delete_custos(request, page_id):
    if request.method == 'POST':
        custos_id = str(request.POST.get('id'))

        p = get_object_or_404(Page, pk=page_id)
        fname = p.get_job_path(j, 'mei')

        md = ModifyDocument(fname)
        md.delete_custos(custos_id)
        md.write_doc()

        return {}
