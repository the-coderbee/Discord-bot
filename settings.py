import os
import pathlib
import logging
from logging.config import dictConfig

import discord
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_COLOR = discord.Color.from_rgb(77, 255, 255)

# Database
db_name = os.getenv('DATABASE_NAME')
db_host = os.getenv('DATABASE_HOST')
db_port = os.getenv('DATABASE_PORT')
db_user = os.getenv('DATABASE_USER')
db_pass = os.getenv('DATABASE_PASS')

# Directories
BASE_DIR = pathlib.Path(__file__).parent
COGS_DIR = BASE_DIR / 'cogs'
DB_DIR = BASE_DIR / 'database'
IMG_DIR = BASE_DIR / 'images'
TEMP_AVT_DIR = IMG_DIR / 'temp_avatars'
STATIC_IMG_DIR = IMG_DIR / 'static_images'

# lavalink
l_host = 'localhost'
l_port = 2333
l_pass = os.getenv('LAVALINK_PASSWORD')
l_region = 'asia'
l_name = 'default-node'

# logging config
LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s",
        },
        "standard": {
            "format": "%(levelname)-10s - %(name)-15s : %(message)s",
        },
    },
    "handlers": {
        "console": {
            'level': "DEBUG",
            'class': "logging.StreamHandler",
            'formatter': "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/info.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {
            'handlers': ['console'],
            'level': "INFO",
            'propagate': False,
        },
        "discord": {
            'handlers': ['console', 'file'],
            'level': "INFO",
            'propagate': False,
        },
    },
}

dictConfig(LOGGING_CONFIG)
