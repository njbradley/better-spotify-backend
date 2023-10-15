from django.http import HttpResponse, HttpResponseRedirect
from .models import SpotifyBackend

def login(request):
    user = request.user
    current_backend = user.getMusicBackend()

    if current_backend is not None:
        return HttpResponse("You are already signed into spotify. Redirecting you back")

    backend = SpotifyBackend(user)
    redirect_url = backend.login(reverse('spotify-callback'))
    return HttpResponseRedirect(redirect_url)

def loginCallback(request):
    user = request.user
    current_backend = user.getMusicBackend()
    
    callback_url = reverse('spotify-callback')
    backend.loginCallback(callback_url, request.url)


