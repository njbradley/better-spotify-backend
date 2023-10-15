


def play(request):
  backend = request.user.getMusicBackend;
  #  request.data = json object
  # request.song_id
  # request.playback is timing
  id = request.data["song_id"]
  pos = request.data["position"]
  song = Song.objects.get(uid = id)
  backend.play(song, pos * 1000)

def pause(request):
  request.user.getMusicBackend.pause()


def status(request):
  return 

