# SuperRareBot

![Example Discord message](screenshot.png?raw=true "Example Discord message")

## Prerequisites

- Python 3.9
- [Poetry](https://python-poetry.org/)
- [Firefox](https://www.mozilla.org/en-GB/firefox/)
- [Gecko Driver](https://github.com/mozilla/geckodriver/releases) is available in your PATH

## Installation

Install dependencies using `poetry install`.

Create an `.env` file in the root of this repository. Here is an example:

```
# Required
DISCORD_BOT_TOKEN = r4EqT6uYIoghdb634GdfgvweFDgrter
DISCORD_CHANNEL_ID = 001122334455667788
DISCORD_SERVER_ID = 887766554433221100
SUPERRARE_ARTIST = bottoproject

# Optional
UPDATE_INTERVAL = 5
```

When you have created your `.env` file, run the bot using `poetry run python main.py`

By default the bot will check for updates every 5 minutes. This can be configured by changing the value of `UPDATE_INTERVAL`.

## How it works

This bot will periodically fetch the latest SuperRare data from an artist of your choice using a headless browser. It will then compare this data to the locally stored data (`db.json`). If there is new data available, messages will be sent to a Discord channel of your choice to notify everyone of updates (new bids, auction ended, etc).

## Why was this created

To notify members of the [Botto](https://botto.com/) Discord when new bids have been placed, auctions had started or ended, or when new pieces have been minted. However, the bot is written in such a way that it can be used for any SuperRare artist.
