import logging

from superrarebot.config import DEBUG, DISCORD_BOT_TOKEN, verify_config
from superrarebot.discord import bot

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("superrarebot.log"), logging.StreamHandler()],
)


if __name__ == "__main__":
    verify_config()
    bot.run(DISCORD_BOT_TOKEN)
