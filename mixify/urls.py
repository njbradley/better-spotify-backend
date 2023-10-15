"""
URL configuration for mixify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import apis, views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    path("api/playback/play", apis.play),
    path("api/playback/pause", apis.pause),
    path("api/playback/state", apis.state),
    
    path("api/search", apis.search),

    #path("api/userTags", apis.getUserTags)
    #path("api/userSongs", apis.getUserSongs)

    #path("api/tags", apis.getTag),
    #path("api/tag/list", apis.getTag),
    #path("api/tag/create", apis.createTag),
    #path("api/tag/add", apis.addTag),
    #path("api/tag/remove", apis.addTag),

    #path("api/tag/", apis.listTags),
    #path("api/tag/<name>", apis.tagApi),

    path("spotify/", include("spotify_backend.urls")),

    path("", views.homepage),

    #path("api/tags/", apis.tags),
    #path("api/tags/<tagid>", apis.tags),
    #path("api/query", apis.query),
]
