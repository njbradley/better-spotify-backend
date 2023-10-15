from urllib.parse import urlencode
from django.db import models
from ..musicbackend import MusicBackend
from ..models import Song
import requests
import requests.oath2
import os

class SpotifySong(models.Model):
    song = models.ForeignKey(Song, on_delete=models.PROPAGATE)
    spotify_id = models.CharField(max_length=255)


# Handles Spotify Backend methods.    
class SpotifyBackend(MusicBackend):
    code = models.CharField(max_length=255)

    # Add the spotify account:
    #   - Authorize user.
    #   - Get authentication token.
    #   - A
    def login(self, user, callback_url):

        api_url = 'https://accounts.spotify.com/authorize'
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']
        scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private'
        state = '132456'

        self.oauth = OAuth2Session(client_id, redirect_uri='https://127.0.0.1:8080/callback', scope=scope)
        auth_url, state = self.oauth.authorization_url(api_url, state=state)

        def loginCallback(self, request, callback_url):
            token = self.oauth.fetch_token(
                'https://accounts.spotify.com/api/token',
                authorization_response=request.url,
                client_secret=client_secret)

        return auth_url, self.loginCallback


        

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

    def search_spotify(self, query, token, type="track", limit=10):
        base_url = "https://api.spotify.com/v1/search"
        
        params = {
            "q": query,
            "type": type,
            "limit": limit
        }
        
        response = self.oauth.get(base_url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
