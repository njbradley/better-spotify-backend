from rest_framework.response import Response as RestResponse
from rest_framework.decorators import api_view
from .models import Tag
from .models import TaggedSong
from .models import Song
import requests


@api_view(['POST'])
def login_api(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    token = Token.objects.get(user=user).key


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
def state(request):
  song, curpos = request.user.getMusicBackend().state()
  return RestResponse({"song": song.uid, "position": curpos, "duration": song.duration})


@api_view(http_method_names=['GET', 'POST', 'PUT', 'DELETE'])
def tagApi(request, name=None, id=None):
    if name is not None:
        tag = Tag.objects.get(user=request.user, name=name)
    if id is not None:
        tag = Tag.objects.get(id=id)

    songs = None
    if 'song' in request.data:
        songs = [Song.objects.get(uid=request.data['uid'])]
    if 'songs' in request.data:
        songs = [Song.objects.get(uid=uid) for uid in request.data['songs']]

    if request.method == 'GET':
        songs = TaggedSong.objects.filter(tag=tag).values_list('song').values()
        return RestResponse(list(songs))

    if request.method == 'POST':
        pass



@api_view(http_method_names=['PUT'])
def createTag(request):
    query = Tag.objects.filter(user=request.user, name=request.data['name'])
    if query.count() == 0:
        tag = Tag(request.user, request.data["name"])
        tag.save()
        return RestResponse({"status": "success"})

    return RestResponse({"status": "unchanged"})

@api_view(http_method_names=['PUT'])
def addTag(request):
  tag = Tag.objects.get(user=request.user, name=request.data['tag'])
  song = Song.objects.get(uid=request.data['song'])
  query = TaggedSong.filter(tag=tag, song=song)

  if query.count() == 0:
      tag_song = TaggedSong(tag=tag, song=song)
      tag_song.save()
      return RestResponse({"status": "success"})
  return RestResponse({"status": "unchanged"})

@api_view(http_method_names=['POST'])
def search(request):
  query = request.data['query']
  songs, playlists = request.user.getMusicBackend().search(query)
  tags = findTags(request.user, query)
  data = convertSongToTrackObject(songs)
  data['numTracks'] = len(songs)
  data['playlists'] = playlists
  data['numPlaylists'] = len(playlists)
  data['tags'] = []
  for index, tag in enumerate(tags):
    data['tags'].append({})
    data['tags'][index]['name'] = tags[index].name
  return RestResponse(data)

def convertSongToTrackObject(songs):
  data = {}
  data['tracks'] = []
  for index, song in enumerate(songs):
    data['tracks'].append({})
    data['tracks'][index]["albumArt"] = song.album_art
    data['tracks'][index]["artistsNames"] = [song.artist]
    data['tracks'][index]['duration'] = song.duration
    data['tracks'][index]["playable"] = True
    data['tracks'][index]["name"] = song.name
    data['tracks'][index]["uuid"] = song.uid

  return data


def findTags(user, query) -> list[Tag]:
  new_tag = Tag.objects.filter(user=user)
  words = query.split()
  new_tag = new_tag.filter(name__icontains=words[0])
  for i in range(1, len(words)):
    new_tag = new_tag | new_tag.filter(name__icontains=words[i])
  
  return list(new_tag)



@api_view(http_method_names=['DELETE'])
def removeTag(request):
  tag = Tag.objects.get(user=request.user, name=request.data['tag'])
  song = Song.objects.get(uid=request.data['song'])
  query = TaggedSong.filter(tag=tag, song=song)

  if query.count() == 0:
      tag_song = TaggedSong(tag=tag, song=song)
      tag_song.save()
      return RestResponse({"status": "success"})

  return RestResponse({"status": "unchanged"})

@api_view(http_method_names=['GET'])
def getTag(request):
    if 'id' in request.data:
        tag = Tag.get(id=request.data['id'])
    else:
        tag = Tag.get(user=request.user, name=request.data['name'])
    songs = TaggedSong.objects.filter(tag=tag).values_list('song').values()
    return RestResponse({'id': tag.id, 'name': name, 'songs': songs})

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
def get_songid_from_tag(uid, tag):
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

