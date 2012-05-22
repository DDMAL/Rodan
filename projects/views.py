# Create your views here.
from django.shortcuts import render

def dashboard(request):
    data = {}
    return render(request, 'projects/dashboard.html', data)

def create(request):
    data = {}
    return render(request, 'projects/create.html', data)

def settings(request):
    data = {}
    return render(request, 'projects/settings.html', data)

def status(request):
    data = {}
    return render(request, 'projects/status.html', data)
