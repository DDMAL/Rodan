from django.shortcuts import render


def crop(request):
    print "Crop called"
    data = {
        "image": "http://placehold.it/1024x1024"  # a placeholder image for now
    }
    return render(request, 'jobs/crop.html', data)
