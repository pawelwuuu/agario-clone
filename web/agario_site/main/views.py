from django.shortcuts import render

def index(request):
    return render(request, 'main/index.html')

def download(request):
    return render(request, 'main/download.html')