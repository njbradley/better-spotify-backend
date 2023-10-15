from ..musicbackend import MusicBackend
from ..models import Song
import spotipy

# Handles Spotify Backend methods.    
class SpotifyBackend(MusicBackend):

    def __init__(self):
        self.sp = spotipy.Spotify()


    # Add the spotify account:
    #   - Authorize user.
    #   - Get authentication token.
    #   - A
    def login(self, user):
        pass

    # Plays "song" in spotify from "time" ms.
    # Sends song duration to 
    def play(self, song: Song, start_time: int):
        
        self.sp.start_playback(uris=[song], position_ms=start_time)

    def pause(self):
        pass

    def currentState(self) -> (Song, int, int):
        pass

    