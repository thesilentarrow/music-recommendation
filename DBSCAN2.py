# import libraries
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.cluster import DBSCAN
import numpy as np

# initialize spotipy client with your credentials
client_id = "00597080cc594010b69e8406c08edfa3"
client_secret = "165ccddc2e04454cbd0da4ee29bfd667"
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# get a list of tracks from a playlist
playlist_id = "37i9dQZF1DXcBWIGoYBM5M" # example playlist id
results = sp.playlist_tracks(playlist_id)
tracks = results["items"]

# get audio features for each track
features = []
ids = []
for track in tracks:
    id = track["track"]["id"]
    ids.append(id)
    feature = sp.audio_features(id)[0]
    if isinstance(feature, list) and feature:
        feature = feature[0]
    # check if feature is a dictionary
    if isinstance(feature, dict):
        features.append(feature)
# convert features to numpy array
features = np.array(features)

# perform DBSCAN clustering on features
dbscan = DBSCAN(eps=0.5, min_samples=5)
print(features)
dbscan.fit(features)

# get cluster labels for each track
labels = dbscan.labels_

# ask user for a song name
song_name = input("Enter a song name: ")

# search for the song on Spotify
results = sp.search(q=song_name, limit=1)
if results["tracks"]["total"] == 0:
    print("Sorry, no song found.")
else:
    # get the id and features of the first result
    song_id = results["tracks"]["items"][0]["id"]
    song_features = sp.audio_features(song_id)[0]

    # predict the cluster label for the song
    song_label = dbscan.predict([song_features])[0]

    # find the tracks that have the same cluster label
    similar_tracks = []
    for i in range(len(labels)):
        if labels[i] == song_label:
            similar_tracks.append(ids[i])

    # randomly select five tracks from the similar tracks
    recommendations = np.random.choice(similar_tracks, 5, replace=False)

    # print the recommendations
    print("Here are five songs you might like:")
    for id in recommendations:
        track = sp.track(id)
        name = track["name"]
        artist = track["artists"][0]["name"]
        print(f"{name} by {artist}")