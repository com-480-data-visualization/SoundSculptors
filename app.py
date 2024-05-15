import spotipy
from flask import Flask, session, request, redirect, jsonify
from flask_session import Session
from spotipy.oauth2 import SpotifyClientCredentials
import os
import country_converter as coco
from collections import Counter
import json


cc = coco.CountryConverter()

app = Flask(__name__)

os.environ['SPOTIPY_CLIENT_ID'] = '88eec4f7753e4dfca4df81e895266679'
os.environ['SPOTIPY_CLIENT_SECRET'] = '23952bdbe81c4618b3950b4bf321da2b' #or as environment variables
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
os.environ["SPOTIPY_REDIRECT_URI"] = 'http://localhost:5000'
os.environ["PORT"] = "5001"
#Session(app)

client_credentials_manager = SpotifyClientCredentials(client_id='88eec4f7753e4dfca4df81e895266679', client_secret='23952bdbe81c4618b3950b4bf321da2b')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_tracks(playlist_id):
    # Get tracks from the playlist
    tracks = sp.playlist_tracks(playlist_id, limit=50)['items']
    # Extract track IDs
    track_ids = [track['track']['id'] for track in tracks if track['track']]
    return track_ids
def get_top_tracks_playlist_id(country_name):
    # Search for the top tracks playlist for the country
    playlist = sp.search("Top 50 - " + country_name, limit=1, type="playlist")
    if playlist['playlists']['items']:
        # Extract the top tracks playlist ID
        playlist_id = playlist['playlists']['items'][0]['uri']
        return playlist_id
    else:
        return None

print("Start cache initing")

country_top_sound_ids = {}

# for country_code in sp.country_codes:
for country_code in sp.available_markets()['markets']:
    country_name = coco.convert(country_code, to="name_short", not_found="Global")
    playlist_id = get_top_tracks_playlist_id(country_name)
    if playlist_id is None:
        continue
    country_top_sound_ids[country_code] = get_playlist_tracks(playlist_id)


print("Init cache done!")

@app.route('/radar_similarity', methods=['GET'])
def get_radar_data():
    country_code = request.args.get('country_code')

    # Get list of track IDs for the input country
    input_country_tracks = country_top_sound_ids.get(country_code, [])
    if not input_country_tracks:
        return jsonify({"error": "No tracks found for the input country"}), 404

    try:
        # Calculate track feature similarity for input country tracks
        similarity_scores = calculate_average_track_features(input_country_tracks)

        return jsonify(similarity_scores), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def calculate_average_track_features(track_ids):
    # Dictionary to store average features
    average_features = {
        "acousticness": 0,
        "danceability": 0,
        "duration_ms": 0,
        "energy": 0,
        "speechiness": 0,
        "tempo": 0
    }

    # Get track features for input country tracks
    for track_id in track_ids:
        track_features = sp.audio_features(track_id)[0]
        if track_features:
            average_features["acousticness"] += track_features["acousticness"] or 0
            average_features["danceability"] += track_features["danceability"] or 0
            average_features["duration_ms"] += track_features["duration_ms"] or 0
            average_features["energy"] += track_features["energy"] or 0
            average_features["speechiness"] += track_features["speechiness"] or 0
            average_features["tempo"] += track_features["tempo"] or 0

    # Calculate average features
    num_tracks = len(track_ids)
    if num_tracks > 0:
        for feature in average_features:
            average_features[feature] /= num_tracks
            average_features[feature] = round(average_features[feature], 3)

    return average_features

@app.route('/music_similarity', methods=['GET'])
def get_music_similarity():
    # Get country code from request parameters
    country_code = request.args.get('country_code')

    try:
        country_name = coco.convert(country_code, to="name_short", not_found="Global")
    except coco.CountryNotFoundException:
        return jsonify({"error": "Invalid country code"}), 400

    try:
        similarity_scores = calculate_similarity(country_code)

        return jsonify(similarity_scores), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/top_genres', methods=['GET'])
def get_top_genres_api():
    # Get country code from request parameters
    country_code = request.args.get('country_code')

    try:
        # Convert country code to country name
        country_name = coco.convert(country_code, to="name_short", not_found="Global")
    except coco.CountryNotFoundException:
        return jsonify({"error": "Invalid country code"}), 400

    try:
        # Get top genres for the country
        top_genres = get_top_genres(country_code)
        return app.response_class(
            response=json.dumps(top_genres, sort_keys=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_top_genres(country_name):
    playlist = sp.search("Top 50 - " + country_name, limit=1, type="playlist")

    if not playlist['playlists']['items']:
        raise Exception("Top tracks playlist does not exist")

    playlist_id = playlist['playlists']['items'][0]['uri']
    top_tracks = sp.playlist_tracks(playlist_id, limit=50)['items']

    # Extract artist IDs from each track
    artist_ids = [track['track']['artists'][0]['id'] for track in top_tracks]

    # Fetch genres of artists
    genres = []
    for artist_id in artist_ids:
        artist_info = sp.artist(artist_id)
        if artist_info['genres']:
            genres.extend(artist_info['genres'])

    # Calculate genre distribution
    genre_counts = Counter(genres)
    total_artists = len(artist_ids)
    genre_distribution = {genre: (count / total_artists) * 100 for genre, count in genre_counts.items()}

    total_percentage = sum(genre_distribution.values())
    normalized_genre_distribution = {genre: round((percentage / total_percentage) * 100, 1) for genre, percentage in
                                     genre_distribution.items()}

    sorted_genres = sorted(normalized_genre_distribution.items(), key=lambda x: x[1], reverse=True)

    top_10_genres = dict(sorted_genres[:10])

    return top_10_genres

def calculate_similarity(country_code):
    similarity_scores = {}
    global country_top_sound_ids
    current_country_top_sound_ids = country_top_sound_ids[country_code]
    for cc, tracks in country_top_sound_ids.items():
        if cc != country_code:
            try:
                # Get top tracks playlist ID for another country
                # other_country_name = coco.convert(cc, to="name_short", not_found="Global")
                # other_playlist_id = get_top_tracks_playlist_id(other_country_name)

                # Get tracks from both playlists
                country_tracks = set(current_country_top_sound_ids)
                other_country_tracks = set(tracks)

                # Calculate Jaccard similarity coefficient
                similarity_score = len(country_tracks.intersection(other_country_tracks)) / len(
                    country_tracks.union(other_country_tracks))

                similarity_score = round(similarity_score, 3)
                # Store similarity score
                similarity_scores[cc] = similarity_score
            except Exception as e:
                print(f"Error calculating similarity with country {cc}: {e}")
    return similarity_scores

@app.route('/top_tracks', methods=['GET'])
def get_top_tracks():
    # Get country code from request parameters
    country_code = request.args.get('country_code')

    try:
        # Convert country code to country name
        country_name = coco.convert(country_code, to="name_short", not_found="Global")
    except coco.CountryNotFoundException:
        return jsonify({"error": "Invalid country code"}), 400

    try:
        # Search for the top tracks playlist for the country
        playlist = sp.search("Top 50 - " + country_name, limit=1, type="playlist")
        if playlist['playlists']['items']:
            # Extract the top tracks playlist ID
            playlist_id = playlist['playlists']['items'][0]['uri']
            # Get tracks from the playlist
            tracks = sp.playlist_tracks(playlist_id, limit=50)['items']
            # Extract relevant information about the tracks
            top_tracks = [{
                "name": track['track']['name'],
                "artist": track['track']['artists'][0]['name'],
                "popularity": track['track']['popularity']
            } for track in tracks]
            return jsonify(top_tracks), 200
        else:
            return jsonify({"error": "Top tracks playlist not found for the country"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/artist_details', methods=['GET'])
def get_artist_details():
    # Get artist name from request parameters
    artist_name = request.args.get('artist_name')

    try:
        # Search for the artist
        results = sp.search(artist_name, limit=1, type="artist")

        if results['artists']['items']:
            # Get the first artist from the search results
            artist = results['artists']['items'][0]

            # Extract relevant information
            follower_number = artist['followers']['total']
            popularity = artist['popularity']
            image_url = artist['images'][0]['url'] if artist['images'] else None

            # Get the artist's albums
            albums = sp.artist_albums(artist['id'], album_type='album')
            album_number = len(albums['items'])

            # Get related artists
            related_artists = []
            for related_artist in sp.artist_related_artists(artist['id'])['artists']:
                related_artists.append(related_artist['name'])

            # Construct the response JSON
            response_data = {
                "follower_number": follower_number,
                "popularity": popularity,
                "image_url": image_url,
                "album_number": album_number,
                "related_artists": related_artists
            }

            return app.response_class(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json'
            )
        else:
            return jsonify({"error": "Artist not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT")))