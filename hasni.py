import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import itertools
import pandas as pd

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials())

# 1 - Build a population of artists
artist_map = {
    "6AqjzYRx9TeJDzKhkSSHFx": "Cheb Hasni"
}

# 1.5 - Get basic artist info (Monthly listeners for instance)
selected_artists = spotify.artists(artist_map.keys()).get("artists")

# 2 - Get their top tracks
def get_track_id(track):
    return track.get("id")


all_tracks = list()
for artist_id in artist_map.keys():
    artist_albums = spotify.artist_albums(artist_id).get("items")
    for album in artist_albums:
        album_tracks = spotify.album_tracks(album.get("id")).get("items")
        full_tracks = spotify.tracks(list(map(get_track_id, album_tracks)))
        for track in full_tracks.get("tracks"):
            track["main_artist"] = artist_map.get(artist_id)
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

af = pd.DataFrame(audio_features)
tt = pd.DataFrame(all_tracks)

df = pd.merge(tt, af, how="left", on="id")
df = df[['id', 'name', 'main_artist', 'key', 'mode', 'time_signature', 'duration_ms_x', 'danceability', 'loudness', 'energy', 'instrumentalness', 'liveness', 'valence', 'speechiness', 'tempo','popularity']]
df = df.sort_values(by=['popularity'], ascending=False)

df.to_csv("hasni.csv", index=False)