from urllib.parse import urlencode
from django.db import models
from mixify.models import Song, MusicBackend
import requests
from requests_oauthlib import OAuth2Session
import os
import secrets

class SpotifySong(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255)


# Handles Spotify Backend methods.    
class SpotifyBackend(MusicBackend):
    token = models.JSONField(null=True)
    state = models.CharField(max_length=16)

    authorize_url = 'https://accounts.spotify.com/authorize'
    token_url = 'https://accounts.spotify.com/api/token'
    scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private'

    def __init__(self, *args, **kwargs):
        super(SpotifyBackend, self).__init__(*args, **kwargs)
        if self.token != None:
            self.oauth = self.get_oauth()

    # Add the spotify account:
    #   - Authorize user.
    #   - Get authentication token.
    #   - A
    def login(self, callback_url):
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']
        self.state = secrets.token_hex(16)

        oauth = OAuth2Session(self.client_id, redirect_uri=callback_url, scope=self.scope)
        auth_url, state = self.oauth.authorization_url(api_url, state=self.state)

        return auth_url

    def loginCallback(self, callback_url, request_url):
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']

        oauth = OAuth2Session(self.client_id, redirect_uri=callback_url, scope=self.scope)
        auth_url, state = self.oauth.authorization_url(api_url, state=self.state)
        token = oauth.fetch_token(
            self.token_url,
            authorization_response=request.url,
            client_secret=client_secret)
        self.token = token
        self.save()

        self.oauth = self.get_oauth()

        return auth_url, loginCallback
    
    def get_oauth(self):
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']
    
        def save_token(token):
            self.token = token
            self.save()

        oauth = OAuth2Session(client_id, token=self.token, auto_refresh_url=self.token_url,
            auto_refresh_kwargs=dict(client_id=client_id, client_secret=client_secret), token_updater=save_token)
        return oauth

    # Plays "song" in spotify from "time" ms.
    # Sends song duration to 
    def play(self, song: Song, start_time: int):
        api_url = "https://api.spotify.com/v1/me/player/play"
        uri = "spotify:track:" + lookupSong(song).spotify_id
        request_body = {
            "uris": uri,
            "position_ms": start_time
        }
        response = requests.put(api_url, json=request_body)
        status_code = response.status_code()
        if status_code != 200:
            response.raise_for_status()
        

    # Pauses the current song in play.
    def pause(self):
        api_url = "https://api.spotify.com/v1/me/player/pause"
        response = requests.put(api_url)
        status_code = response.status_code()
        if status_code != 200:
            response.raise_for_status()

    # Get Playback state returns -> (song, curr_pos, duration)
    def currentState(self) -> (Song, int, int):
        api_url = "https://api.spotify.com/v1/me/player/currently-playing"

        response = requests.get(api_url)
        status_code = response.status_code
        if response.status_code == 200:
            # Device currently active
            json = response.json()
            curr_pos_ms = int(json["progress_ms"])
            duration_ms = int(json["item"]["duration_ms"])
            song = SpotifySong.objects.filter(spotify_id=json['item']['id'])
            return (song, curr_pos_ms, duration_ms)
        else:
            response.raise_for_status()

    
    # Looks up for song in SpotifySong database.
    # If found, then return SpotifySong database entry(each song is unique).
    # Otherwise, it adds a new song into the SpotifySong database and 
    # then returns the entry.
    # If no song is found in spotify's database, return None.
    def lookupSong(song: Song) -> SpotifySong:
        # look up song in database
        query = SpotifySong.objects.filter(song=song)
        if query.size() > 0:
            return query[0]
        
        # lookup from spotify api if have name alternative, fun
        artist = song.artist
        track = song.name
        api_url = "https://api.spotify.com/v1/search"
        params = {"q": {"artist": artist, "track": track}}
        response = self.oauth.get(api_url, params=params)
        status_code = response.status_code()
        if status_code == 200:
            json = response.json()
            if json['tracks']['total'] > 0:
                return SpotifySong.objects.create(song=song, spotify_id=json['tracks']['items']['id'])
        else:
            response.raise_for_status()

        return None

    def search_spotify(self, query, token, type="track", limit=10):
        base_url = "https://api.spotify.com/v1/search"
        
        params = {
            "q": query,
            "type": type,
            "limit": limit
        }
        
        response = self.oauth.get(base_url, params=params)

        if response.status_code == 200:
            return response.json()    # return everything?
        else:
            response.raise_for_status()

