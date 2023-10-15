from django.db import models
from ..musicbackend import MusicBackend
from ..models import Song
import requests

class SpotifySong(models.Model):
    song = models.ForeignKey(Song, on_delete=models.PROPAGATE)
    spotify_id = models.CharField(max_length=255)


# Handles Spotify Backend methods.    
class SpotifyBackend(MusicBackend):

    # Add the spotify account:
    #   - Authorize user.
    #   - Get authentication token.
    #   - A
    def login(self, user):
        pass

    # Plays "song" in spotify from "time" ms.
    # Sends song duration to 
    def play(self, song: Song, start_time: int, retries=0):
        api_url = "https://api.spotify.com/v1/me/player/play"
        request_body = {
            "uris": lookupSong(song).spotify_id,
            "position_ms": start_time
        }
        response = requests.put(api_url, json=request_body)
        status_code = response.status_code()
        if status_code == 401:
            # access token expire
            self.authenticateToken()
            if retries < 2:
                self.play(self, song, start_time, retries+1)
            else:
                raise RuntimeError("Too many re-authentications")
        elif status_code == 403:
            # Bad OAuth request
            raise RuntimeError("Bad OAuth request")
        elif status_code == 429:
            # The app has exceeded its rate limits.
            raise RuntimeError("The app has exceeded its rate limits.")
        

    # Pauses the current song in play.
    def pause(self, retries=0):
        api_url = "https://api.spotify.com/v1/me/player/pause"
        response = requests.put(api_url)
        status_code = response.status_code()
        if status_code == 401:
            self.authenticateToken()
            if retries < 2:
                self.pause(self, retries+1)
            else:
                raise RuntimeError("Too many re-authentications")
        elif status_code == 403:
            # Bad OAuth request
            raise RuntimeError("Bad OAuth request")
        elif status_code == 429:
            # The app has exceeded its rate limits.
            raise RuntimeError("The app has exceeded its rate limits.")

    # Get Playback state returns -> (song, curr_pos, duration)
    def currentState(self) -> (Song, int, int):
        api_url = "https://api.spotify.com/v1/me/player/currently-playing"
        response = requests.get(api_url)
        if response.status_code == 200:
            # Device currently active
            curr_pos_ms = int(response.json()["progress_ms"])
            duration_ms = int(response.json()["item"]["duration_ms"])
            

    def authenticateToken():
        pass

    
    # Looks up for song in SpotifySong database.
    # If found, then return SpotifySong database entry(each song is unique).
    # Otherwise, it adds a new song into the SpotifySong database and 
    # then returns the entry.
    def lookupSong(song: Song) -> SpotifySong:
        # look up song in database
        query = SpotifySong.objects.filter(song=song)
        if query.size() > 0:
            return query[0]
        
        # lookup from spotify api, fun
        

        pass

