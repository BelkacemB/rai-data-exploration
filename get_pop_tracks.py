import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import itertools
import requests
import json
import urllib.parse
import pandas as pd 
import numpy as np

NO_RESULT = "No results for "

LAST_FM_API_KEY = "72ec1b403f216a7dc7c2cd22bd1dcf51"

def get_last_fm_plays(artist, song):
    
    url = "http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=" + LAST_FM_API_KEY + "&artist="+urllib.parse.quote(artist) + "&track=" + urllib.parse.quote(song) + "&format=json"

    response = requests.get(url)
    dict_response = json.loads(response.text)
    playcount, listeners = 0, 0

    try: 
        playcount, listeners = int(dict_response['track']['playcount']), int(dict_response['track']['listeners'])
    except KeyError: 
        print("Track not found on Last FM.")

    return playcount, listeners

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials())

# 1 - Build a population of artists
artist_map = {
    "7yLOExurLKWUlj520esuAt": "Kamel Messaoudi",
    "73LjFn4z6WTV7MevyPxrRc": "Idir",  
    "2aVPTWc4WYc7b384eatevF": "Didine Canon 16",
}

# 1.5 - Get basic artist info (Monthly listeners for instance)
selected_artists = spotify.artists(artist_map.keys()).get("artists")

# 2 - Get their top tracks
def get_track_id(track):
    return track.get("id")

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
            playcount, listeners = get_last_fm_plays(artist=artist_name, song=track["name"])
            track["last_fm_playcount"] = playcount
            track["last_fm_listeners"] = listeners
            print(track_and_artist + " - Last FM playcount: " + str(playcount) ) 
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
df = df[['id', 'name', 'main_artist', 'key', 'mode', 'time_signature', 'duration_ms_x', 'danceability', 'loudness', 'energy', 'instrumentalness', 'liveness', 'valence', 'speechiness', 'tempo','popularity','last_fm_playcount','last_fm_listeners']]
df = df.sort_values(by=['popularity'], ascending=False)

df.to_csv("pop.csv", index=False)