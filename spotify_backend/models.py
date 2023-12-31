from urllib.parse import urlencode
from django.db import models
from mixify.models import Song, MusicBackend
import requests
from requests_oauthlib import OAuth2Session
import os
import secrets

class SpotifySong(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Handles Spotify Backend methods.    
class SpotifyBackend(MusicBackend):
    token = models.JSONField(null=True)
    state = models.CharField(max_length=16, null=True)
    lastDevice = models.CharField(max_length=127, null=True)

    authorize_url = 'https://accounts.spotify.com/authorize'
    token_url = 'https://accounts.spotify.com/api/token'
    scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private'

    def __init__(self, *args, **kwargs):
        super(SpotifyBackend, self).__init__(*args, **kwargs)
        if self.token != None:
            self.oauth = self.get_oauth()

    # Add the spotify account:
    #   - Authorize user.
    #   - Get authentication token.
    #   - A
    def login(self, callback_url):
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']
        self.state = secrets.token_hex(8)

        oauth = OAuth2Session(client_id, redirect_uri=callback_url, scope=self.scope)
        auth_url, state = oauth.authorization_url(self.authorize_url, state=self.state)

        return auth_url

    def loginCallback(self, callback_url, request_url):
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']

        oauth = OAuth2Session(client_id, redirect_uri=callback_url, scope=self.scope)
        auth_url, state = oauth.authorization_url(self.authorize_url, state=self.state)
        token = oauth.fetch_token(
            self.token_url,
            authorization_response=request_url,
            client_secret=client_secret)
        self.token = token
        self.save()

        self.oauth = self.get_oauth()
    
    def get_oauth(self):
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']
    
        def save_token(token):
            self.token = token
            self.save()

        oauth = OAuth2Session(client_id, token=self.token, auto_refresh_url=self.token_url,
            auto_refresh_kwargs=dict(client_id=client_id, client_secret=client_secret), token_updater=save_token)
        #token = oauth.refresh_token(self.token_url, client_id=client_id, client_secret=client_secret)
        #save_token(token)
        return oauth

    # Plays "song" in spotify from "time" ms.
    # Sends song duration to 
    def play(self, song: Song, start_time: int):
        api_url = "https://api.spotify.com/v1/me/player/play"
        
        #params = {}
        #if self.lastDevice is not None:
            #params = dict(device_id=self.lastDevice)

        uri = "spotify:track:" + self.lookupSong(song).spotify_id
        request_body = {
            "uris": [uri],
            "position_ms": start_time
        }
        response = self.oauth.put(api_url, json=request_body)#, params=params)
        status_code = response.status_code
        if status_code != 204:
            response.raise_for_status()
        

    # Pauses the current song in play.
    def pause(self):
        api_url = "https://api.spotify.com/v1/me/player/pause"
        response = self.oauth.put(api_url)
        status_code = response.status_code
        if status_code != 204:
            response.raise_for_status()

    # Get Playback state returns -> (song, curr_pos, duration)
    def state(self) -> (Song, int):
        api_url = "https://api.spotify.com/v1/me/player/currently-playing"

        response = self.oauth.get(api_url)
        status_code = response.status_code
        if response.status_code == 200:
            # Device currently active
            json = response.json()
            self.save()
            curr_pos_ms = int(json["progress_ms"])
            duration_ms = int(json["item"]["duration_ms"])
            spotify_song = SpotifySong.objects.get(spotify_id=json['item']['id'])

            """
            if 'device' in json:
                self.lastDevice = json["device"]["id"]
            else:
                response2 = self.oauth.get("https://api.spotify.com/v1/me/player/devices")
                if response.status_code == 200:
                    json = response2.json()
                    print (json)
                    for device in json['devices']:
                        if device['is_active']:
                            self.lastDevice = device['id']
                            self.save()
                            break
            """

            return (spotify_song.song, curr_pos_ms)
        else:
            response.raise_for_status()

    def trackObjToSong(self, track):
        name, artist = track['name'], track['artists'][0]['name']
        params = dict(
            duration=track['duration_ms'],
            album_art=self.getBestArt(track['album']['images']),
        )
        return self.reverseLookupSong(track['id'], name, artist, params)
    
    # Looks up for song in SpotifySong database.
    # If found, then return SpotifySong database entry(each song is unique).
    # Otherwise, it adds a new song into the SpotifySong database and 
    # then returns the entry.
    # If no song is found in spotify's database, return None.
    def lookupSong(self, song: Song) -> SpotifySong:
        # look up song in database
        query = SpotifySong.objects.filter(song=song)
        if query.count() > 0:
            return query[0]
        
        # lookup from spotify api if have name alternative, fun
        artist = song.artist
        track = song.name
        api_url = "https://api.spotify.com/v1/search"
        #params = {"q": {"artist": artist, "track": track}}
        params = {"q": artist + ' ' + track, 'type': 'track'}
        response = self.oauth.get(api_url, params=params)
        status_code = response.status_code
        if status_code == 200:
            json = response.json()
            if json['tracks']['total'] > 0:
                tracks = json['tracks']['items']
                spotify_id = tracks[0]['id']
                return SpotifySong.objects.create(song=song, spotify_id=spotify_id)
        else:
            response.raise_for_status()

        return None

    def reverseLookupSong(self, spotify_id, name, artist, params):
        query = SpotifySong.objects.filter(spotify_id=spotify_id)
        if query.count() > 0:
            return query[0].song

        query = Song.objects.filter(name=name, artist=artist)
        if query.count() > 0:
            spotifySong = SpotifySong(song=query[0], spotify_id=spotify_id)
            spotifySong.save()
            return spotifySong.song

        song = Song(uid=name+'__'+artist, name=name, artist=artist, **params)
        song.save()
        spotifySong = SpotifySong(song=song, spotify_id=spotify_id)
        spotifySong.save()
        return song

    def getBestArt(self, images):
        if len(images) == 0: return None
        index = 0
        while (index < len(images)-1 and images[index]['height'] is not None and images[index]['width'] is not None
                and images[index]['width'] > 300 and images[index]['height'] > 300):
            index += 1
        
        return images[index]['url']

    def search(self, query, page=0, pagesize=50):
        base_url = "https://api.spotify.com/v1/search"
        
        params = {
            "q": query,
            "type": 'track,playlist',
            "limit": pagesize,
            "offset": page * pagesize,
        }
        
        response = self.oauth.get(base_url, params=params)

        if response.status_code != 200:
            response.raise_for_status()

        json = response.json()
        tracks = json['tracks']['items']
        songs = []

        for track in tracks:
            name, artist = track['name'], track['artists'][0]['name']
            params = dict(
                duration=track['duration_ms'],
                album_art=track['album']['images'][-1]['url'],
            )

            song = self.reverseLookupSong(track['id'], name, artist, params)
            songs.append(song)

        playlists = json['playlists']['items']
        out_playlists = []

        for playlist in playlists:
            out_playlists.append(dict(
                collaborative=playlist['collaborative'],
                description=playlist['description'],
                image=self.getBestArt(playlist['images']),
                name=playlist['name'],
                owner=dict(
                    username=self.user.username,
                    isFriend=False,
                    profileUri=None,
                    uuid=self.user.id,
                ),
            ))

        return songs, out_playlists

    # Lists all the users playlists from spotify.
    # Return a list of PlayListObject dictionaries.
    def listPlaylists(self) -> dict():
        api_url = "https://api.spotify.com/v1/me/playlists"
        response = self.oauth.get(api_url)
        if response.status_code != 200:
            response.raise_for_status()
        else:
            json = response.json()
            result_list = []
            for i in range(len(json['items'])):
                result_list.append({})
                result_list[i]['collaborative'] = False
                result_list[i]['description'] = json['items'][i]['description']
                result_list[i]['image'] = self.getBestArt(json['items'][i]['images'])
                result_list[i]['name'] = json['items'][i]['name']
                result_list[i]['owner'] = json['items'][i]['owner']
                result_list[i]['uuid'] = json['items'][i]['id']
        
            return result_list

    
    # Takes in a playlists and import them.
    def importPlaylist(self, playlists):
        for i in range(len(playlists)):
            p = playlists[i]
            p_id = p['uuid']
            api_url = f"https://api.spotify.com/v1/playlists/{p_id}"
            response = self.oauth.get(api_url)
            if response.status_code != 200:
                response.raise_for_status()
            else:
                tracks = response.json()['tracks']
                for playlist_track_obj in tracks['items']:
                    track_obj = playlist_track_obj['track']
                    id = track_obj['id']
                    name = track_obj['name']
                    artist = track_obj['artists'][0]['name']
                    self.reverseLookupSong(self, id, name, artist)
