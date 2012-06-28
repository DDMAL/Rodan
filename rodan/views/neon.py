from rodan.utils import render_to_json
from rodan.jobs.modifymei import ModifyDocument
import json

@render_to_json()
def insert_neume(request):
    if request.method == 'POST':
        before_id = str(request.POST['beforeid'])
        pname = str(request.POST['pname'])
        oct = str(request.POST['oct'])
        dot_form = str(request.POST['dotform'])

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''
        
        md = ModifyDocument(fname)
        result = md.insert_punctum(before_id, pname, oct, dot_form, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_neume(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])

        id = str(data["id"])
        before_id = str(data["beforeid"])
        
        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        pitch_info = data["pitchInfo"]

        fname = ''

        md = ModifyDocument(fname)
        md.move_neume(id, before_id, pitch_info, ulx, uly, lrx, lry)
        md.write_doc()

@render_to_json()
def delete_neume(request):
    if request.method == 'POST':
        ids = str(request.POST['ids'])

        fname = ''

        md = ModifyDocument(fname)
        md.delete_neume(ids.split(","))
        md.write_doc()

@render_to_json()
def neumify(request):
    if request.method == 'POST':
        nids = str(request.POST['nids'])
        neume_name = str(request.POST['name'])

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''

        md = ModifyDocument(fname)
        result = md.neumify(nids.split(','), neume_name, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def ungroup(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])

        nids = str(data["nids"])
        bboxes = data["bbs"]

        fname = ''

        md = ModifyDocument(fname)
        result = md.ungroup(nids.split(','), bboxes)
        md.write_doc()

        return result

@render_to_json()
def insert_division(request):
    if request.method == 'POST':
        div_type = str(request.POST['type'])
        before_id = str(request.POST['beforeid'])

        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''

        md = ModifyDocument(fname)
        result = md.insert_division(before_id, div_type, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_division(request):
    if request.method == 'POST':
        id = str(request.POST['id'])
        before_id = str(request.POST['beforeid'])

        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''

        md = ModifyDocument(fname)
        md.move_division(id, before_id, ulx, uly, lrx, lry)
        md.write_doc()

@render_to_json()
def delete_division(request):
    if request.method == 'POST':
        ids = str(request.POST['ids'])

        fname = ''

        md = ModifyDocument(fname)
        md.delete_division(ids.split(","))
        md.write_doc()

@render_to_json()
def insert_dot(request):
    if request.method == 'POST':
        id = str(request.POST['id'])
        dot_form = str(request.POST['dotform'])

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''
        md = ModifyDocument(fname)
        md.add_dot(id, dot_form, ulx, uly, lrx, lry)
        md.write_doc()

@render_to_json()
def delete_dot(request):
    if request.method == 'POST':
        id = str(request.POST['id'])

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''

        md = ModifyDocument(fname)
        md.delete_dot(id, ulx, uly, lrx, lry)
        md.write_doc()

@render_to_json()
def insert_clef(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        shape = str(data["shape"]).upper()
        line = str(data["line"])
        before_id = str(data["beforeid"])

        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''

        md = ModifyDocument(fname)
        result = md.insert_clef(line, shape, data["pitchInfo"], before_id, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_clef(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        clef_id = str(data["id"])
        
        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        line = str(data["line"])

        fname = ''

        md = ModifyDocument(fname)
        md.move_clef(clef_id, line, data["pitchInfo"], ulx, uly, lrx, lry)
        md.write_doc()

@render_to_json()
def update_clef_shape(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        clef_id = str(data["id"])

        try:
            ulx = str(data["ulx"])
            uly = str(data["uly"])
            lrx = str(data["lrx"])
            lry = str(data["lry"])
        except KeyError:
            ulx = uly = lrx = lry = None

        shape = str(data["shape"])

        fname = ''

        md = ModifyDocument(fname)
        md.update_clef_shape(clef_id, shape, data["pitchInfo"], ulx, uly, lrx, lry)
        md.write_doc()

@render_to_json()
def delete_clef(request):
    if request.method == 'POST':
        clefs_to_delete = json.loads(request.POST['data'])

        fname = ''

        md = ModifyDocument(fname)
        md.delete_clef(clefs_to_delete)
        md.write_doc()

@render_to_json()
def insert_custos(request):
    if request.method == 'POST':
        pname = str(request.POST['pname'])
        oct = str(request.POST['oct'])
        before_id = str(request.POST['beforeid'])

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''

        md = ModifyDocument(fname)
        result = md.insert_custos(pname, oct, before_id, ulx, uly, lrx, lry)
        md.write_doc()

        return result

@render_to_json()
def move_custos(request):
    if request.method == 'POST':
        custos_id = str(request.POST['id'])
        pname = str(request.POST['pname'])
        oct = str(request.POST['oct'])

        try:
            ulx = str(request.POST['ulx'])
            uly = str(request.POST['uly'])
            lrx = str(request.POST['lrx'])
            lry = str(request.POST['lry'])
        except KeyError:
            ulx = uly = lrx = lry = None

        fname = ''

        md = ModifyDocument(fname)
        md.move_custos(custos_id, pname, oct, ulx, uly, lrx, lry)
        md.write_doc()

@render_to_json()
def delete_custos(request):
    if request.method == 'POST':
        custos_id = str(request.POST['id'])

        fname = ''

        md = ModifyDocument(fname)
        md.delete_custos(custos_id)
        md.write_doc()
