from rest_framework.views import api_view
from rest_framework.response import RestResponse
from .models import Tag
from .models import TaggedSong

@api_view()
def play(request):
  backend = request.user.getMusicBackend;
  #  request.data = json object
  # request.song_id
  # request.playback is timing
  id = request.data["song_id"]
  pos = request.data["position"]
  song = Song.objects.get(uid = id)
  backend.play(song, pos * 1000)

@api_view()
def pause(request):
  request.user.getMusicBackend.pause()

@api_view()
def status(request):
  return 


def create_tag(request):
  tag = Tag(request.user, request.data["tag_name"])
  tag.save()

def add_tag_son(request):
  tag_song = TaggedSong(request.data["tag"], request.data["song"])
  tag_song.save()