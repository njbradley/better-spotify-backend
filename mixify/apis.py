from rest_framework.response import Response as RestResponse
from rest_framework.decorators import api_view
from .models import Tag
from .models import TaggedSong
import requests

@api_view()
def play(request):
  backend = request.user.getMusicBackend()
  #  request.data = json object
  # request.song_id
  # request.playback is timing
  id = request.data["song"]
  pos = request.data["position"]
  song = Song.objects.get(uid = id)
  backend.play(song, pos)

@api_view()
def pause(request):
  request.user.getMusicBackend().pause()

@api_view()
def status(request):
  return 


def create_tag(request):
  tag = Tag(request.user, request.data["tag_name"])
  tag.save()

def add_tag_son(request):
  tag_song = TaggedSong(request.data["tag"], request.data["song"])
  tag_song.save()

# get all songs with tag
# get tag from user

def get_playlist_details(request):
    user_id = "Our user ID"
    playlist_id = "YOUR_PLAYLIST_ID"
    token = "YOUR_OAUTH_TOKEN"
    url = f"https://api.spotify.com/{user_id}/playlists/{playlist_id}"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# # Usage
# playlist_details = get_playlist_details(playlist_id, token)
# print(playlist_details)

# get name, id, and uri
def search_spotify(query, token, type="track", limit=10):
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