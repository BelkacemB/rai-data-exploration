import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import itertools
import pandas as pd 
import numpy as np
import urllib.parse
import requests
import json

NO_RESULT = "No results for "
# Do not forget so space out the requests
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials())

# 1 - Build a population of artists

artist_map = {
    "49uZa5QPkhpwmHXs2LVtBi": "Cheikh el Hasnaoui",
    "0WtlXlCzfp2mJyINCsf1tb": "Dahmane El Harrachi",  
    "4sgdpsrVemff9aGDauF4J4": "El Hachemi Guerouabi",
    "2tCdo4TZ9Fz8eidDpdhlBl": "Amar Ezzahi",
    "7yLOExurLKWUlj520esuAt": "Kamel Messaoudi",
    "7qTOODbVqiOKADjo82VHAw": "Abdelkader Chaou",
    "5r8pbzFmhj7W5GVntzws4g": "Naima Dziria"
}

# 1.5 - Get basic artist info (Monthly listeners for instance)
# 1.5 - Get basic artist info (Monthly listeners for instance)
selected_artists = spotify.artists(artist_map.keys()).get("artists")

# 2 - Get their top tracks
def get_track_id(track):
    return track.get("id")

def get_youtube_views(search):
    url = "http://youtube-scrape.herokuapp.com/api/search?q=" + urllib.parse.quote(search)
    json_response = requests.get(url)
    dict_response = json.loads(json_response.text)
    try:
        views_text = dict_response["results"][0]["video"]["views"]
    except KeyError:
        print(NO_RESULT + search)
        return 0
    except IndexError: 
        print(NO_RESULT + search)
        return 0
    try:
        result = int(views_text[:-6].replace(",",""))
    except ValueError: 
        print(NO_RESULT + search)
        return 0

    return result 

all_tracks = list()
for artist_id in artist_map.keys():
    artist_name = artist_map.get(artist_id)
    artist_albums = spotify.artist_albums(artist_id).get("items")
    for album in artist_albums:
        album_tracks = spotify.album_tracks(album.get("id")).get("items")
        full_tracks = spotify.tracks(list(map(get_track_id, album_tracks)))
        for track in full_tracks.get("tracks"):
            track["main_artist"] = artist_name
            track_and_artist = (track["name"] + " " + artist_name)
            track["youtube_views"] = get_youtube_views(track_and_artist)
            print(track_and_artist + " - Youtube views: " + str(track["youtube_views"]) )
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

# 4 - Store the data in a CSV file
# 5 - Create a notebook and explore the data

af = pd.DataFrame(audio_features)
tt = pd.DataFrame(all_tracks)

df = pd.merge(tt, af, how="left", on="id")
df = df[['id', 'name', 'main_artist', 'key', 'mode', 'time_signature', 'duration_ms_x', 'danceability', 'loudness', 'energy', 'instrumentalness', 'liveness', 'valence', 'speechiness', 'tempo','popularity','youtube_views']]
df = df.sort_values(by=['popularity'], ascending=False)

df.to_csv("chaabi.csv", index=False)