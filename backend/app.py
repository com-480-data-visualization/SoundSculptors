import os

from SpotifyHandler import SpotifyHandler
from HttpHandler import HttpHandler
from config import AppConfig

# cc = coco.CountryConverter()
#
# app = Flask(__name__)
#
# os.environ['SPOTIPY_CLIENT_ID'] = '88eec4f7753e4dfca4df81e895266679'
# os.environ['SPOTIPY_CLIENT_SECRET'] = '23952bdbe81c4618b3950b4bf321da2b' #or as environment variables
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_FILE_DIR'] = './.flask_session/'
# os.environ["SPOTIPY_REDIRECT_URI"] = 'http://localhost:5000'
# os.environ["PORT"] = "5001"
# #Session(app)
#
# client_credentials_manager = SpotifyClientCredentials(client_id='88eec4f7753e4dfca4df81e895266679', client_secret='23952bdbe81c4618b3950b4bf321da2b')
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


if __name__ == '__main__':
    config = AppConfig()
    config.initialize()

    sp = SpotifyHandler(config.SPOTIPY_CLIENT_ID, config.SPOTIPY_CLIENT_SECRET)
    app = HttpHandler(config.PORT, sp)

    app.run()
