
from SpotifyHandler import SpotifyHandler
from HttpHandler import HttpHandler
from config import AppConfig


if __name__ == '__main__':
    config = AppConfig()
    config.initialize()

    sp = SpotifyHandler(config.SPOTIPY_CLIENT_ID, config.SPOTIPY_CLIENT_SECRET)
    app = HttpHandler(config.PORT, sp)

    app.run()
