import logging
from typing import Any

import yaml
from loguru import logger
from pydantic import BaseModel, validator

class AppConfig(BaseModel):

    def initialize(self, config_file='config.yaml'):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        self.SPOTIPY_CLIENT_ID = config['SPOTIPY_CLIENT_ID']
        self.SPOTIPY_CLIENT_SECRET = config['SPOTIPY_CLIENT_SECRET']
        self.SPOTIPY_REDIRECT_URI = config['SPOTIPY_REDIRECT_URI']
        self.SESSION_TYPE = config['SESSION_TYPE']
        self.SESSION_FILE_DIR = config['SESSION_FILE_DIR']
        self.PORT = config['PORT']
        self.LOGGING_LEVEL = config.get('LOGGING_LEVEL', 'INFO')

    def configure_logging(self):
        logging.basicConfig(level=self.LOGGING_LEVEL,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')