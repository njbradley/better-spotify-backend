from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import staticfiles

@login_required()
def homepage(request):
    return HttpResponse("Hello")

def frontend(request, path=""):
    return staticfiles.views.serve(request, "mixify/build/index.html")

def frontend_assets(request, path=""):
    return staticfiles.views.serve(request, "mixify/build/assets/" + path)

def frontend_logo(request, path=""):
    return staticfiles.views.serve(request, "mixify/build/logo.svg")
