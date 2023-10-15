from django.http import HttpResponse, HttpResponseRedirect
from .models import SpotifyBackend
from django.urls import reverse

def login(request):
    user = request.user
    current_backend = user.getMusicBackend()

    if current_backend is not None:
        print (current_backend.token)
        return HttpResponse("You are already signed into spotify. Redirecting you back")

    backend = SpotifyBackend(user=user)
    redirect_url = backend.login('http://127.0.0.1:8000' + reverse('spotify-callback'))
    backend.save()
    return HttpResponseRedirect(redirect_url)

def loginCallback(request):
    user = request.user
    backend = user.getMusicBackend()
    
    callback_url = 'http://127.0.0.1:8000' + reverse('spotify-callback')
    backend.loginCallback(callback_url, request.build_absolute_uri())
    return HttpResponse('logged in!')


