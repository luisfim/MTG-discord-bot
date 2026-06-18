# MTG Digital Updates

A Discord bot that tracks MTG Arena and Magic Online updates, patch notes, server status, and announcements.
The bot currently supports MTG Arena and Magic Online update links, with planned features for automatic notifications, summaries, maintenance alerts, and event tracking.

## Features

Current commands:

- `/ping` — checks if the bot is online
- `/arena_latest` — shows the official MTG Arena patch notes page or latest detected patch note
- `/mtgo_latest` — shows the latest Magic Online announcement or official MTGO news page
- `/digital_magic_latest` — shows both MTG Arena and MTGO updates in one embed
- `/arena_status` — shows the MTG Arena service status page
- `/mtgo_status` — shows the Magic Online server status page
- `/set_updates_channel` — sets the channel for automatic Magic updates
- `/set_update_sources` — chooses whether the server receives Arena updates, MTGO updates, or both
- `/update_settings` — shows the server’s current update settings
- `/send_test_update` — sends a test update to the configured channel
- `/check_updates_now` — manually runs the automatic update checker

## Automatic Updates

The bot can automatically check for new digital Magic updates every few hours.

Server admins can configure:

- which channel receives updates
- whether MTG Arena updates are enabled
- whether Magic Online updates are enabled

The bot stores the last detected Arena and MTGO update URLs locally in SQLite, so it does not repeatedly post the same update.


## Why this bot exists

MTG Arena and Magic Online updates are posted in different places. This bot aims to bring digital Magic updates into one Discord assistant for players who want quick access to patch notes, announcements, maintenance status, and event information.

## Tech Stack

- Python
- discord.py
- aiohttp
- BeautifulSoup
- python-dotenv
- SQLite

## Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/MTG-discord-bot.git
cd MTG-discord-bot