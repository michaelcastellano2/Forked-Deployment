from django.shortcuts import render


def index(request):
    return render(request, "collabrate/index.html")

def login(request):
    return render(request, "collabrate/login.html")

def register(request):
    return render(request, "collabrate/register.html")