import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import itertools
import requests
import json
import urllib.parse
# Do not forget so space out the requests
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials())

# 1 - Build a population of artists
artist_map = {
    "11E9GHIAzJRKuECEUSEuqh": "Cheb Bello",
    "3e3cKwH1kUr02bvIm7VaIe": "Kader Japonais",
    "5CZ5sGdn0X47HhndSYKqdz": "Cheba Dalila",
    "0c3dDCJfxcT4lYNugbKvJt": "Warda",
    "4iCrZzxACYPYcoS71DgjWW": "Bilal Sghir",
    "59N7N5tX53jyPhAmsRi4or": "Cheb Bilal",
    "4ZzMtjQsjtaAOm3GPqmjeQ": "Cheb Djalil"
}

# 1.5 - Get basic artist info (Monthly listeners for instance)
selected_artists = spotify.artists(artist_map.keys()).get("artists")

# 2 - Get their top tracks
def get_track_id(track):
    return track.get("id")

def get_youtube_views(search):
    url = "http://youtube-scrape.herokuapp.com/api/search?q=" + urllib.parse.quote(search)
    json_response = requests.get(url)
    dict_response = json.loads(json_response.text)
    views_text = dict_response["results"][0]["video"]["views"]
    result = int(views_text[:-6].replace(",",""))
    return result 

all_tracks = list()
for artist_id in artist_map.keys():
    artist_albums = spotify.artist_albums(artist_id).get("items")
    for album in artist_albums:
        album_tracks = spotify.album_tracks(album.get("id")).get("items")
        full_tracks = spotify.tracks(list(map(get_track_id, album_tracks)))
        for track in full_tracks.get("tracks"):
            artist_name = artist_map.get(artist_id)
            track["main_artist"] = artist_name
            track["youtube_views"] = get_youtube_views(track["name"] + " " + artist_name )
            all_tracks.append(track)

# 3 - Get maximum track features
tracks_ids = list(map(get_track_id, all_tracks))


def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk

audio_features = list()

for track_ids_chunk in chunked_iterable(tracks_ids, 99):
    audio_features.extend(spotify.audio_features(tracks=track_ids_chunk))

