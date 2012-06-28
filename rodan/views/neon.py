from rodan.utils import render_to_json

@render_to_json()
def edit(request):
    return {"x": range(10)}
