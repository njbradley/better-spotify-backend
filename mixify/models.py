from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    def getMusicBackend(self):
        from spotify_backend.models import SpotifyBackend
        musicBackends = [SpotifyBackend]

        for backend in musicBackends:
            query = backend.objects.filter(user=self)
            if query.count() != 0:
                return query[0]

class Song(models.Model):
    uid = models.CharField(max_length=127)
    name = models.CharField(max_length=127)
    artist = models.CharField(max_length=127)
    album_art = models.URLField(max_length=255, null=True)
    duration = models.IntegerField()

    def __str__(self):
        return "Song '" + self.uid + "'"

class Tag(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=127)

    def __str__(self):
        return "Tag " + self.user.username + " " + self.name

class TaggedSong(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    def __str__(self):
        return "TaggedSong " + self.tag.user.username + " " + self.tag.name + " " + self.song.uid


class MusicBackend(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def play(song: Song, start_time: int):
        pass

    def pause():
        pass

    def state() -> (Song, int):
        pass

    def search():
        pass

    def listPlaylists():
        pass

    def importPlaylist():
        pass
    
    class Meta:
        abstract = True

