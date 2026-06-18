# Magic Digital Bot

A Discord bot for tracking official digital Magic: The Gathering updates.

The bot currently supports MTG Arena and Magic Online update links, with planned features for automatic notifications, summaries, maintenance alerts, and event tracking.

## Features

Current commands:

- `/ping` — checks if the bot is online
- `/arena_latest` — shows the official MTG Arena patch notes page or latest detected patch note
- `/mtgo_latest` — shows the latest Magic Online announcement or official MTGO news page
- `/digital_magic_latest` — shows both MTG Arena and MTGO updates in one embed

## Why this bot exists

MTG Arena and Magic Online updates are posted in different places. This bot aims to bring digital Magic updates into one Discord assistant for players who want quick access to patch notes, announcements, maintenance status, and event information.

## Tech Stack

- Python
- discord.py
- aiohttp
- BeautifulSoup
- python-dotenv

## Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/MTG-discord-bot.git
cd MTG-discord-bot