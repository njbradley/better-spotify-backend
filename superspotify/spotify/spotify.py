from urllib.parse import urlencode
from ..musicbackend import MusicBackend
from ..models import Song
import requests
import requests.oath2
import os

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
            "uris": song,
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

            


    def pause(self):
        pass

    def currentState(self) -> (Song, int, int):
        pass

    def authenticateToken():
        pass

    
