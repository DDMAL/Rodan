# Create your views here.
from django.shortcuts import render

def dashboard(request):
    data = {}
    return render(request, 'projects/dashboard.html', data)

def create(request):
    data = {}
    return render(request, 'projects/create.html', data)
