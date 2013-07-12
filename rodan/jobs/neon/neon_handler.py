import os
import json
import shutil
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from rodan.models.runjob import RunJob

from rodan.jobs.neon.modifymei import ModifyDocument
from rodan.jobs.neon.utils import render_to_json
from rodan.jobs.neon.utils import live_mei_path, backup_mei_path


@render_to_json()
def insert_neume(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        result = md.insert_punctum(before_id, pname, oct, dot_form, ulx, uly, lrx, lry)
        md.write_doc()

        return result


@render_to_json()
def move_neume(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.move_neume(id, before_id, pitch_info, ulx, uly, lrx, lry)
        md.write_doc()

        return {}


@render_to_json()
def delete_neume(request, runjob_id):
    if request.method == 'POST':
        ids = str(request.POST.get('ids'))

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.delete_neume(ids.split(","))
        md.write_doc()

        return {}


@render_to_json()
def update_neume_head_shape(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.update_neume_head_shape(id, head_shape, ulx, uly, lrx, lry)
        md.write_doc()

        return {}


@render_to_json()
def neumify(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        result = md.neumify(nids, type_id, head_shapes, ulx, uly, lrx, lry)
        md.write_doc()

        return result


@render_to_json()
def ungroup(request, runjob_id):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])

        nids = str(data.get("nids"))
        bboxes = data.get("bbs")

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        result = md.ungroup(nids.split(','), bboxes)
        md.write_doc()

        return result


@render_to_json()
def insert_division(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        result = md.insert_division(before_id, div_type, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_division(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.move_division(id, before_id, ulx, uly, lrx, lry)
        md.write_doc()

        return {}


@render_to_json()
def delete_division(request, runjob_id):
    if request.method == 'POST':
        ids = str(request.POST.get('ids'))

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.delete_division(ids.split(","))
        md.write_doc()

        return {}


@render_to_json()
def insert_dot(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.add_dot(id, dot_form, ulx, uly, lrx, lry)
        md.write_doc()

        return {}


@render_to_json()
def delete_dot(request, runjob_id):
    if request.method == 'POST':
        id = str(request.POST.get('id'))

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.delete_dot(id, ulx, uly, lrx, lry)
        md.write_doc()

        return {}


@render_to_json()
def insert_clef(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        result = md.insert_clef(line, shape, data["pitchInfo"], before_id, ulx, uly, lrx, lry)
        md.write_doc()

        return result


@render_to_json()
def move_clef(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.move_clef(clef_id, line, data["pitchInfo"], ulx, uly, lrx, lry)
        md.write_doc()

        return {}


@render_to_json()
def update_clef_shape(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.update_clef_shape(clef_id, shape, data["pitchInfo"], ulx, uly, lrx, lry)
        md.write_doc()

        return {}


@render_to_json()
def delete_clef(request, runjob_id):
    if request.method == 'POST':
        clefs_to_delete = json.loads(request.POST['data'])

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.delete_clef(clefs_to_delete)
        md.write_doc()

        return {}


@render_to_json()
def insert_custos(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        result = md.insert_custos(pname, oct, before_id, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_custos(request, runjob_id):
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

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.move_custos(custos_id, pname, oct, ulx, uly, lrx, lry)
        md.write_doc()

        return {}


@render_to_json()
def delete_custos(request, runjob_id):
    if request.method == 'POST':
        custos_id = str(request.POST.get('id'))

        runjob = get_object_or_404(RunJob, pk=runjob_id)
        fname = live_mei_path(runjob)

        md = ModifyDocument(fname)
        md.delete_custos(custos_id)
        md.write_doc()

        return {}

@render_to_json()
def revert_file(request, runjob_id):
    if request.method == 'GET':
        runjob = get_object_or_404(RunJob, pk=runjob_id)
        print backup_mei_path(runjob)
        print os.path.exists(backup_mei_path(runjob))
        if os.path.exists(backup_mei_path(runjob)):
            shutil.copy(backup_mei_path(runjob), live_mei_path(runjob))

        else:
         raise Http404
