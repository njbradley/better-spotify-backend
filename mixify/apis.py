from rest_framework.response import Response as RestResponse
from rest_framework.decorators import api_view
from .models import Tag
from .models import TaggedSong
from .models import Song
import requests

#import redis

#r = redis.Redis(
  #host='redis-11191.c27688.us-east-1-mz.ec2.cloud.rlrcp.com',
  #port=11191,
  #password='8tqBgsB0gBKeGaexEmq4RhLWMe2Pnzqg')

@api_view(http_method_names=['POST'])
def play(request):
  backend = request.user.getMusicBackend()
  #  request.data = json object
  # request.song
  # request.playback is timing
  id = request.data["song"]
  pos = request.data["position"]
  print (id)
  song = Song.objects.get(uid = id)
  backend.play(song, pos)
  return RestResponse({"status": "success"})

@api_view(http_method_names=['PUT'])
def pause(request):
  request.user.getMusicBackend().pause()
  return RestResponse({"status": "success"})

@api_view(http_method_names=['GET'])
def status(request):
  song, curpos, duration = request.user.getMusicBackend().currentState()
  return RestResponse({"song": song.uid, "position": curpos, "duration": duration})


def create_tag(request):
  tag = Tag(request.user, request.data["tag_name"])
  tag.save()

def create_tagged_song(request):
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

# given user id and name of tag, return the id of songs
def get_tag(uid, tag):
  tags = Tag.objects.get(uid=uid, name=tag)
  taggedSongs = TaggedSong.objects.filter(tag=tags)
  uids = []

  for taggedSong in taggedSongs:
    uids.append(taggedSong.song.uid)
  
  return uids

# given id of songs, return song
def get_song(uids = []):
   songs: Song = []
   for uid in uids:
      songs.append(Song.objects.get(uid))
   return songs




