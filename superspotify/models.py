from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class Song(models.Model):
    uid = models.CharField()
    name = models.CharField(max_length=127)
    artist = models.CharField(max_length=127)

class Tag(models.Model):
    user = models.ForeignKey(CustomUser)
    name = models.CharField(max_length=127)

class TaggedSong(models.Model):
    tag = models.ForeignKey(Tag)
    song = models.ForeignKey(Song)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=127)
    musicBackends = [SpotifyBackend]

    def getMusicBackend(self):
        for backend in self.musicBackends:
            pass

class MusicBackend(models.Model):
    user = model.ForeignKey(CustomUser)

    def login(user):
        pass

    def play(song: Song, start_time: int):
        pass

    def pause():
        pass

    def currentState() -> (Song, int):
        pass
    
    class Meta:
        abstract = False

