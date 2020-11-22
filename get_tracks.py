import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Do not forget so space out the requests
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials())

# 1 - Build a population of artists
artist_ids = [
    "11E9GHIAzJRKuECEUSEuqh",
    "3e3cKwH1kUr02bvIm7VaIe",
    "5CZ5sGdn0X47HhndSYKqdz",
    "0c3dDCJfxcT4lYNugbKvJt",
    "4iCrZzxACYPYcoS71DgjWW",
    "59N7N5tX53jyPhAmsRi4or",
    "4ZzMtjQsjtaAOm3GPqmjeQ"
]

# 1.5 - Get basic artist info (Monthly listeners for instance)
selected_artists = spotify.artists(artist_ids).get("artists")

# 2 - Get their top tracks
top_tracks = list()
for artist_id in artist_ids:
    artist_top_tracks = spotify.artist_top_tracks(artist_id).get("tracks")
    top_tracks.extend(artist_top_tracks)

print(top_tracks)
# 3 - Get maximum track features
# 4 - Store the data in a CSV file
# 5 - Create a notebook and explore the data
