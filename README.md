# MTG Digital Updates

A Discord bot that tracks **MTG Arena** and **Magic Online** updates, patch notes, server status, and announcements.

[Add MTG Digital Updates to your Discord server](https://discord.com/oauth2/authorize?client_id=1516867226433622146&permissions=84992&scope=bot%20applications.commands)

## Features

* Fetches the latest MTG Arena patch notes
* Fetches the latest Magic Online announcements
* Checks MTG Arena server status
* Checks Magic Online server status
* Sends update embeds to a configured Discord channel
* Lets server admins choose which update sources are enabled
* Stores server settings locally with SQLite
* Runs automatic update checks to avoid repeated posts

## Commands

| Command                 | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| `/ping`                 | Checks if the bot is online                              |
| `/arena_latest`         | Shows the latest MTG Arena patch note                    |
| `/mtgo_latest`          | Shows the latest Magic Online announcement               |
| `/digital_magic_latest` | Shows the latest updates from both MTG Arena and MTGO    |
| `/arena_status`         | Shows MTG Arena server status                            |
| `/mtgo_status`          | Shows Magic Online server status                         |
| `/set_updates_channel`  | Sets the channel where automatic updates will be posted  |
| `/set_update_sources`   | Chooses whether Arena, MTGO, or both sources are enabled |
| `/update_settings`      | Shows the current server update settings                 |
| `/send_test_update`     | Sends a test update to the configured channel            |
| `/check_updates_now`    | Manually runs the update checker                         |
| `/about`                | Shows information about the bot                          |
| `/help`                 | Shows available commands                                 |

## Tech Stack

* Python
* discord.py
* aiohttp
* BeautifulSoup
* python-dotenv
* SQLite
* AWS Lightsail
* systemd
  
## Local Setup

Clone the repository:

```bash
git clone https://github.com/luisfim/MTG-discord-bot.git
cd MTG-discord-bot
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```bash
cp .env.example .env
```

Add your Discord bot token to `.env`:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

Run the bot:

```bash
python bot.py
```

## Automatic Updates

Server admins can configure a channel for automatic updates using:

```text
/set_updates_channel
```

They can also choose which sources are enabled:

```text
/set_update_sources
```

The bot stores the latest detected update URLs in a local SQLite database to avoid posting the same update repeatedly.

## Roadmap

* Improve MTG Arena patch note summaries
* Improve Magic Online status detection
* Add MTG Arena maintenance alerts
* Add Magic Online Treasure Chest update detection
* Add event schedule tracking
* Add admin command to change automatic check frequency
* Add richer patch note summaries
