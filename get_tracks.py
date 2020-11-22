import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# 1 - Build a population of artists 
# 1.5 - Get basic artist info (Monthly listeners for instance)
# 2 - Get their top tracks 
# 3 - Get maximum track features
# 4 - Store the data in a CSV file 
# 5 - Create a notebook and explore the data 