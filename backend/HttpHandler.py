import json

import country_converter as coco
from flask import Flask, request, jsonify

import SpotifyHandler


class HttpHandler:

    def __init__(self, port, spotify_handler: SpotifyHandler):
        self.app = Flask(__name__)
        self.port = port
        self.spotify_handler = spotify_handler



    def run(self):
        @self.app.route('/top_tracks', methods=['GET'])
        def get_top_tracks():
            country_code = request.args.get('country_code')

            try:
                country_name = coco.convert(country_code, to="name_short", not_found="Global")
                top_tracks = self.spotify_handler.get_top_tracks_by_country(country_name)

                return jsonify(top_tracks), 200

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/artist_details', methods=['GET'])
        def get_artist_details():
            artist_name = request.args.get('artist_name')

            try:
                response_data = self.spotify_handler.get_artist_details(artist_name)
                return self.app.response_class(
                    response=json.dumps(response_data),
                    status=200,
                    mimetype='application/json'
                )

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/top_genres', methods=['GET'])
        def get_top_genres_api():
            country_code = request.args.get('country_code')
            try:
                country_name = coco.convert(country_code, to="name_short", not_found="Global")

                top_genres = self.spotify_handler.get_top_genres(country_code)
                return self.app.response_class(
                    response=json.dumps(top_genres, sort_keys=False),
                    status=200,
                    mimetype='application/json'
                )

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/radar_similarity', methods=['GET'])
        def get_radar_data():
            country_code = request.args.get('country_code')

            try:
                similarity_scores = self.spotify_handler.calculate_average_track_features(country_code)

                return jsonify(similarity_scores), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/music_similarity', methods=['GET'])
        def get_music_similarity():
            # Get country code from request parameters
            country_code = request.args.get('country_code')

            try:
                country_name = coco.convert(country_code, to="name_short", not_found="Global")
                similarity_scores = self.spotify_handler.calculate_similarity(country_code)

                return jsonify(similarity_scores), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500


        self.app.run(threaded=True, port= self.port)