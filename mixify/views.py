from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import staticfiles

@login_required()
def homepage(request):
    return HttpResponse("Hello")

def frontend(self, request, path):
    return staticfiles.views.serve(request, "mixify/build/index.html")
