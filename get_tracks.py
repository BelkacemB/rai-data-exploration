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
    "28ztjHIXceRRntmTUfnmUX": "Khaled",
    "11E9GHIAzJRKuECEUSEuqh": "Cheb Bello",  
    "3e3cKwH1kUr02bvIm7VaIe": "Kader Japonais",
    "5CZ5sGdn0X47HhndSYKqdz": "Cheba Dalila",
    "0c3dDCJfxcT4lYNugbKvJt": "Warda",
    "4iCrZzxACYPYcoS71DgjWW": "Bilal Sghir",
    "59N7N5tX53jyPhAmsRi4or": "Cheb Bilal",
    "4ZzMtjQsjtaAOm3GPqmjeQ" : "Cheb Djalil",
    "4l3uOQQa1NaZz7OVNAjbC2": "Cheb Houssem",
    "2zjXHi6RZyaS2t0P1BrxBs": "Cheb Mourad",
    "6AqjzYRx9TeJDzKhkSSHFx": "Cheb Hasni",
    "6vZXamchcIOKzC1c3Elp4J": "Cheb Mami", 
    "364dHqe2BwXqmOhgdBXpw8": "Cheikha Rimitti"
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
df = df[['id', 'name', 'main_artist', 'key', 'mode', 'time_signature', 'duration_ms_x', 'danceability', 'loudness', 'energy', 'instrumentalness', 'liveness', 'valence', 'speechiness', 'tempo','popularity','youtube_views','last_fm_playcount','last_fm_listeners']]
df = df.sort_values(by=['popularity'], ascending=False)

df.to_csv("rai.csv", index=False)