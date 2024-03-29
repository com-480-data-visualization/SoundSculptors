import spotipy
from flask import Flask, session, request, redirect
from flask_session import Session
from spotipy.oauth2 import SpotifyClientCredentials
import os
import country_converter as coco

cc = coco.CountryConverter()

app = Flask(__name__)



app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
os.environ["SPOTIPY_REDIRECT_URI"] = 'http://localhost:5000'
os.environ["PORT"] = "5000"
Session(app)


@app.route('/')
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                               cache_handler=cache_handler,
                                               show_dialog=True)
    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
        f'<a href="/current_user">me</a>' \



@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')

   
@app.route('/popular', methods=["GET", "POST"])
def popular():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    countries = spotify.country_codes
    countries = "\n".join([f"<option value={x}>{cc.convert(x, to="name_short")} </option>" for x in countries])
    form =  f"""
        </form>
     <form id="country" method="POST">

   <label for="countries">Choose a country name:</label> 
    <select name="country" id="country" form="country"> 
        {countries}
    </select>
        <input form=country type="submit">
    """
    if len(request.form) == 0:
        return form
    country_code = request.form["country"]
    country = cc.convert(country_code, to="name_short")

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    
    playlist = spotify.search("Top 50 - " + country, limit=1, type="playlist")
    top_songs = playlist['playlists']['items'][0]['uri']
    # top_songs = spotify.playlist_tracks(top_songs_uri)
    # print(country_code, [x["name"] + " " + x["id"] for x in spotify.categories(country="fr", locale="en_fr")["categories"]["items"]])
    # top_songs =  spotify.category_playlists("0JQ5DAudkNjCgYMM0TZXDw", country=country_code)["playlists"]["items"][0]["uri"]
    # return spotify.playlist_tracks(top_songs)["items"]
    songs = spotify.playlist_tracks(top_songs)
    print(songs)
    return form +f"<h1>Most popular hits in: {country}</h1> <ul>" +"\n".join(["<li>"+x["track"]["name"] + " by " + x['track']["artists"][0]["name"] + "</li>" for x in songs["items"]]) + "</ul>"


@app.route('/find_artist')
def artist():
    return """<form method="POST">
    <input name="text">
    <input type="submit">
    </form>"""
@app.route('/find_artist', methods=["POST"])
def artist_post():
    text = request.form['text']
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    artist_id = spotify.search(text,type='artist', limit=1)['artists']['items'][0]['uri']
    tracks = spotify.artist_albums(artist_id)
    answer = "<ul>"
    for track in tracks['items'][:10]:
        name = 'track    : ' + track['name']
        artist = ' by : ' + track['artists'][0]['name']

        answer += "<li>" + name + artist+ "</li>"
    answer += "</ul>"
    return answer

@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()



if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT")))