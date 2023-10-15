from rest_framework.response import Response as RestResponse
from rest_framework.decorators import api_view

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
    backend = request.user.getMusicBackend()
    song, curpos, duration = backend.currentState()
    return RestResponse({"song": song.uid, "position": curpos, "duration": duration})

