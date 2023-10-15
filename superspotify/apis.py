from rest_framework.views import api_view
from rest_framework.response import RestResponse

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

