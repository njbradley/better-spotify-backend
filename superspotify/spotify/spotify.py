from ..musicbackend import MusicBackend
from ..models import Song
import requests

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