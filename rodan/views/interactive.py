from django.shortcuts import render


def crop(request):
    data = {
        "image": "http://placehold.it/1000x1000"  # a placeholder image for now
    }
    return render(request, 'jobs/crop.html', data)


def binarise(request):
    data = {
        "original_image": "http://placehold.it/1000x1000",  # a placeholder image for now
        "small_thumbnail": "http://placehold.it/150x150",
    }
    return render(request, 'jobs/simple-binarise.html', data)


def despeckle(request):
    data = {
        "original_image": "http://placehold.it/1000x1000",  # a placeholder image for now
        "small_thumbnail": "http://placehold.it/150x150",
    }
    return render(request, 'jobs/despeckle.html', data)


def rotate(request):
    data = {
        "image": "http://placehold.it/1000x1000"  # a placeholder image for now
    }
    return render(request, 'jobs/rotate.html', data)


def segment(request):
    data = {
        "image": "http://placehold.it/1000x1000"  # a placeholder image for now
    }
    return render(request, 'jobs/segmentation.html', data)


def luminance(request):
    data = {
        "medium_thumbnail": "http://placehold.it/400x400",  # a placeholder image for now
    }
    return render(request, 'jobs/luminance.html', data)


def barlinecorrection(request):
    data = {
        "original_image": "http://placehold.it/1000x1000",  # a placeholder image for now
        "small_thumbnail": "http://placehold.it/150x150",
    }
    return render(request, 'jobs/barline-correction.html', data)
