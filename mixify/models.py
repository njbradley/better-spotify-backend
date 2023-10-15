from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    def getMusicBackend(self, user):
        from .spotify.spotify import SpotifyBackend
        musicBackends = [SpotifyBackend]

        for backend in self.musicBackends:
            query = backend.objects.filter(user=user)
            if query.count() != 0:
                return backend

class Song(models.Model):
    uid = models.CharField(max_length=127)
    name = models.CharField(max_length=127)
    artist = models.CharField(max_length=127)

class Tag(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=127)

class TaggedSong(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)


class MusicBackend(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def login(user):
        pass

    def play(song: Song, start_time: int):
        pass

    def pause():
        pass

    def currentState() -> (Song, int):
        pass
    
    class Meta:
        abstract = True
