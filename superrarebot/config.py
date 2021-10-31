import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

DEBUG = os.getenv("DEBUG") == "True"

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))
DISCORD_SERVER_ID = int(os.getenv("DISCORD_SERVER_ID", 0))
SUPERRARE_ARTIST = os.getenv("SUPERRARE_ARTIST")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 5))


def verify_config():
    if not DISCORD_BOT_TOKEN:
        raise Exception("DISCORD_BOT_TOKEN is not set")

    if not DISCORD_CHANNEL_ID:
        raise Exception("DISCORD_CHANNEL_ID is not set")

    if not DISCORD_SERVER_ID:
        raise Exception("DISCORD_SERVER_ID is not set")

    if not SUPERRARE_ARTIST:
        raise Exception("SUPERRARE_ARTIST is not set")

    if UPDATE_INTERVAL < 1:
        raise Exception("UPDATE_INTERVAL needs to be at least 1")
