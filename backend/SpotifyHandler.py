import logging
import country_converter as coco
from collections import Counter
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy


class SpotifyHandler:

    def __init__(self, client_id, client_secret):
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.logger = logging.getLogger(__name__)
        self.country_top_sound_ids = {}
        self.initialize_cache()

    def initialize_cache(self):
        self.logger.info("Cache initialization...")
        for country_code in self.sp.available_markets()['markets']:
            country_name = coco.convert(country_code, to="name_short", not_found="Global")
            playlist_id = self.get_top_tracks_playlist_id(country_name)
            if playlist_id is None:
                continue
            self.country_top_sound_ids[country_code] = self.get_playlist_tracks(playlist_id)

        self.logger.info("Cache initialized")

    def get_playlist_tracks(self, playlist_id):
        tracks = self.sp.playlist_tracks(playlist_id, limit=50)['items']
        track_ids = [track['track']['id'] for track in tracks if track['track']]
        return track_ids

    def get_top_tracks_playlist_id(self, country_name):
        playlist = self.sp.search("Top 50 - " + country_name, limit=1, type="playlist")
        if playlist['playlists']['items']:
            playlist_id = playlist['playlists']['items'][0]['uri']
            return playlist_id
        else:
            return None

    def get_top_tracks_by_country(self, country_name):
        playlist_id = self.get_top_tracks_playlist_id(country_name)
        tracks = self.sp.playlist_tracks(playlist_id, limit=50)['items']
        return [{
            "name": track['track']['name'],
            "artist": track['track']['artists'][0]['name'],
            "popularity": track['track']['popularity']
        } for track in tracks]

    def calculate_average_track_features(self, country_code):
        input_country_tracks = self.country_top_sound_ids.get(country_code, [])

        if not input_country_tracks:
            raise Exception("Tracks does not exist")

        average_features = {
            "acousticness": 0,
            "danceability": 0,
            "duration_ms": 0,
            "energy": 0,
            "speechiness": 0,
            "tempo": 0
        }

        track_feature_list = self.sp.audio_features(input_country_tracks)

        for track_feature in track_feature_list:
            average_features["acousticness"] += track_feature["acousticness"] or 0
            average_features["danceability"] += track_feature["danceability"] or 0
            average_features["duration_ms"] += track_feature["duration_ms"] or 0
            average_features["energy"] += track_feature["energy"] or 0
            average_features["speechiness"] += track_feature["speechiness"] or 0
            average_features["tempo"] += track_feature["tempo"] or 0

        num_tracks = len(input_country_tracks)
        if num_tracks > 0:
            for feature in average_features:
                average_features[feature] /= num_tracks
                average_features[feature] = round(average_features[feature], 3)

        return average_features

    def get_artist_details(self, artist_name):
        results = self.sp.search(artist_name, limit=1, type="artist")

        if results['artists']['items']:
            artist = results['artists']['items'][0]
            follower_number = artist['followers']['total']
            popularity = artist['popularity']
            image_url = artist['images'][0]['url'] if artist['images'] else None

            albums = self.sp.artist_albums(artist['id'], album_type='album')
            album_number = len(albums['items'])

            related_artists = []
            for related_artist in self.sp.artist_related_artists(artist['id'])['artists']:
                related_artists.append(related_artist['name'])

            # Construct the response JSON
            return {
                "follower_number": follower_number,
                "popularity": popularity,
                "image_url": image_url,
                "album_number": album_number,
                "related_artists": related_artists
            }

    def get_top_genres(self, country_name):
        playlist = self.sp.search("Top 50 - " + country_name, limit=1, type="playlist")

        if not playlist['playlists']['items']:
            raise Exception("Top tracks playlist does not exist")

        playlist_id = playlist['playlists']['items'][0]['uri']
        top_tracks = self.sp.playlist_tracks(playlist_id, limit=50)['items']

        # Extract artist IDs from each track
        artist_ids = [track['track']['artists'][0]['id'] for track in top_tracks]

        # Fetch genres of artists
        artist_info_list = self.sp.artists(artist_ids)
        genres = []
        for artist_info in artist_info_list.get("artists"):
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

        max = 10 if len(sorted_genres) > 10 else len(sorted_genres)

        top_10_genres = dict(sorted_genres[:max])

        return top_10_genres

    def calculate_similarity(self, country_code):
        similarity_scores = {}
        current_country_top_sound_ids = self.country_top_sound_ids[country_code]
        for cc, tracks in self.country_top_sound_ids.items():
            if cc != country_code:
                try:
                    country_tracks = set(current_country_top_sound_ids)
                    other_country_tracks = set(tracks)

                    # Calculate Jaccard similarity coefficient
                    similarity_score = len(country_tracks.intersection(other_country_tracks)) / len(
                        country_tracks.union(other_country_tracks))

                    similarity_score = round(similarity_score, 3)
                    # Store similarity score
                    similarity_scores[cc] = similarity_score
                except Exception as e:
                    self.logger.error(f"Error calculating similarity with country {cc}: {e}")
        return similarity_scores
