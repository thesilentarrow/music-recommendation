# Import libraries
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Initialize Spotify API
client_id = "00597080cc594010b69e8406c08edfa3"
client_secret = "165ccddc2e04454cbd0da4ee29bfd667"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Define a function to get audio features of a track
def get_audio_features(track):
    # Get track id
    track_id = sp.search(track, limit=1)["tracks"]["items"][0]["id"]
    # Get audio features
    audio_features = sp.audio_features(track_id)[0]
    # Return a dictionary of audio features
    return {
        "danceability": audio_features["danceability"],
        "energy": audio_features["energy"],
        "loudness": audio_features["loudness"],
        "speechiness": audio_features["speechiness"],
        "acousticness": audio_features["acousticness"],
        "instrumentalness": audio_features["instrumentalness"],
        "liveness": audio_features["liveness"],
        "valence": audio_features["valence"],
        "tempo": audio_features["tempo"]
    }


tracks = ["Bad Habits - Ed Sheeran", 
          "Levitating - Dua Lipa",
          "Blinding Lights - The Weeknd",
          "Happier Than Ever - Billie Eilish",
          "drivers license - Olivia Rodrigo"]
# Define a function to get recommendations based on DBSCAN clustering
def get_recommendations(tracks):
    # Create an empty dataframe to store the tracks and their audio features
    df = pd.DataFrame(columns=["track", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"])
    # For each track, get the audio features and append to the dataframe
    for track in tracks:
        audio_features = get_audio_features(track)
        df = df.append({"track": track, **audio_features}, ignore_index=True)
    # Scale the audio features
    scaler = StandardScaler()
    X = scaler.fit_transform(df.drop("track", axis=1))
    # Fit DBSCAN with eps=0.5 and min_samples=2
    dbscan = DBSCAN(eps=0.3, min_samples=2).fit(X)
    # Get the cluster labels
    labels = dbscan.labels_
    # Get the number of clusters (excluding noise)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    # Print the number of clusters and the tracks in each cluster
    print(f"Number of clusters: {n_clusters}")
    for i in range(n_clusters):
        print(f"Cluster {i}:")
        print(df[labels == i]["track"].to_list())
    # For each cluster, get 5 recommendations from Spotify based on the seed tracks in that cluster
    for i in range(n_clusters):
        print(f"Recommendations for cluster {i}:")
        seed_tracks = df[labels == i]["track"].to_list()
        seed_ids = [sp.search(track, limit=1)["tracks"]["items"][0]["id"] for track in seed_tracks]
        recommendations = sp.recommendations(seed_tracks=seed_ids, limit=5)["tracks"]
        for rec in recommendations:
            print(rec["name"], "-", rec["artists"][0]["name"])
            
get_recommendations(tracks)