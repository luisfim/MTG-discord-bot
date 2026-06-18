import aiohttp
from bs4 import BeautifulSoup

ARENA_PATCH_NOTES_URL = "https://mtgarena-support.wizards.com/hc/en-us/sections/4402585813268-Patch-Notes"
ARENA_STATUS_URL = "https://magicthegatheringarena.statuspage.io/"
MTGO_NEWS_URL = "https://www.mtgo.com/news"
MTGO_HOME_URL = "https://www.mtgo.com/"


async def fetch_html(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 MagicDigitalBot/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        ) as response:
            print(f"Fetching {url} - Status: {response.status}")
            response.raise_for_status()
            return await response.text()


async def get_latest_arena_patch() -> dict:
    try:
        html = await fetch_html(ARENA_PATCH_NOTES_URL)
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.find_all("a", href=True):
            title = link.get_text(" ", strip=True)

            if title.startswith("Patch Notes -"):
                href = link["href"]

                if href.startswith("/"):
                    href = "https://mtgarena-support.wizards.com" + href

                return {
                    "title": title,
                    "url": href,
                    "note": "Latest patch note found automatically.",
                }
    except aiohttp.ClientResponseError as error:
        if error.status == 403:
            print("Arena patch notes page returned 403 Forbidden. Using fallback link.")
            return {
                "title": "MTG Arena Patch Notes",
                "url": ARENA_PATCH_NOTES_URL,
                "note": "Wizards blocked the automatic fetch, so here is the official patch notes page.",
            }

        raise

    except Exception as error:
        print(f"Unexpected Arena fetch error: {error}")
        return {
            "title": "MTG Arena Patch Notes",
            "url": ARENA_PATCH_NOTES_URL,
            "note": "Could not fetch the latest patch automatically, so here is the official patch notes page.",
        }

    return {
        "title": "MTG Arena Patch Notes",
        "url": ARENA_PATCH_NOTES_URL,
        "note": "No patch note title was found automatically, so here is the official patch notes page.",
    }
async def get_latest_mtgo_announcement() -> dict:
    try:
        html = await fetch_html(MTGO_NEWS_URL)
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.find_all("a", href=True):
            title = link.get_text(" ", strip=True)

            if "Weekly Announcements" in title or "Announcements" in title:
                href = link["href"]

                if href.startswith("/"):
                    href = "https://www.mtgo.com" + href

                return {
                    "title": title,
                    "url": href,
                    "note": "Latest Magic Online announcement found automatically.",
                }

    except Exception as error:
        print(f"MTGO fetch error: {error}")
        return {
            "title": "Magic Online News",
            "url": MTGO_NEWS_URL,
            "note": "Could not fetch the latest MTGO announcement automatically, so here is the official MTGO news page.",
        }

    return {
        "title": "Magic Online News",
        "url": MTGO_NEWS_URL,
        "note": "No MTGO announcement title was found automatically, so here is the official MTGO news page.",
    }

async def get_arena_status() -> dict:
    try:
        html = await fetch_html(ARENA_STATUS_URL)
        soup = BeautifulSoup(html, "html.parser")

        status_text = soup.get_text(" ", strip=True)

        if "All Systems Operational" in status_text:
            return {
                "title": "MTG Arena Status",
                "url": ARENA_STATUS_URL,
                "status": "All Systems Operational",
                "note": "The official MTG Arena status page reports that all systems are operational.",
            }

        if "Partial System Outage" in status_text:
            return {
                "title": "MTG Arena Status",
                "url": ARENA_STATUS_URL,
                "status": "Partial System Outage",
                "note": "The official MTG Arena status page reports a partial system outage.",
            }

        if "Major System Outage" in status_text:
            return {
                "title": "MTG Arena Status",
                "url": ARENA_STATUS_URL,
                "status": "Major System Outage",
                "note": "The official MTG Arena status page reports a major system outage.",
            }

        if "Under Maintenance" in status_text:
            return {
                "title": "MTG Arena Status",
                "url": ARENA_STATUS_URL,
                "status": "Under Maintenance",
                "note": "The official MTG Arena status page indicates maintenance.",
            }

        return {
            "title": "MTG Arena Status",
            "url": ARENA_STATUS_URL,
            "status": "Status Unknown",
            "note": "The bot reached the official status page, but could not identify the current status automatically.",
        }

    except Exception as error:
        print(f"Arena status fetch error: {error}")
        return {
            "title": "MTG Arena Status",
            "url": ARENA_STATUS_URL,
            "status": "Could not fetch status",
            "note": "Could not fetch MTG Arena status automatically, so here is the official status page.",
        }
async def get_mtgo_status() -> dict:
    try:
        html = await fetch_html(MTGO_HOME_URL)
        soup = BeautifulSoup(html, "html.parser")

        page_text = soup.get_text(" ", strip=True)

        if "Server Status" in page_text and "Online" in page_text:
            return {
                "title": "Magic Online Server Status",
                "url": MTGO_HOME_URL,
                "status": "Online",
                "note": "The MTGO homepage appears to show the server as online.",
            }

        if "Server Status" in page_text and "Offline" in page_text:
            return {
                "title": "Magic Online Server Status",
                "url": MTGO_HOME_URL,
                "status": "Offline",
                "note": "The MTGO homepage appears to show the server as offline.",
            }

        if "Server Status" in page_text:
            return {
                "title": "Magic Online Server Status",
                "url": MTGO_HOME_URL,
                "status": "Status found, but unclear",
                "note": "The bot found a server status section, but could not confidently read the current status.",
            }

        return {
            "title": "Magic Online Server Status",
            "url": MTGO_HOME_URL,
            "status": "Status unknown",
            "note": "The bot reached the MTGO homepage, but could not find a readable server status value.",
        }

    except Exception as error:
        print(f"MTGO status fetch error: {error}")
        return {
            "title": "Magic Online Server Status",
            "url": MTGO_HOME_URL,
            "status": "Could not fetch status",
            "note": "Could not fetch MTGO status automatically, so here is the official MTGO homepage.",
        }