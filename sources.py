import re
import aiohttp
from bs4 import BeautifulSoup

ARENA_PATCH_NOTES_URL = "https://mtgarena-support.wizards.com/hc/en-us/sections/4402585813268-Patch-Notes"
ARENA_PATCH_NOTES_API_URL = (
    "https://mtgarena-support.wizards.com/api/v2/help_center/en-us/"
    "sections/4402585813268/articles.json"
)
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

async def fetch_json(url: str) -> dict:
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 MagicDigitalBot/1.0",
                "Accept": "application/json",
            },
        ) as response:
            print(f"Fetching JSON {url} - Status: {response.status}")
            response.raise_for_status()
            return await response.json()

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def summarize_article_body(html_body: str, max_items: int = 5) -> str:
    if not html_body:
        return "No readable patch note summary was available."

    soup = BeautifulSoup(html_body, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    important_keywords = [
        "fixed",
        "fix",
        "bug",
        "issue",
        "updated",
        "update",
        "changed",
        "change",
        "new",
        "event",
        "store",
        "card",
        "deck",
        "battlefield",
        "maintenance",
        "resolved",
        "improved",
        "adjusted",
        "banned",
        "suspended",
        "rebalanced",
    ]

    summary_lines = []

    for element in soup.find_all(["h2", "h3", "li", "p"]):
        text = clean_text(element.get_text(" ", strip=True))

        if len(text) < 20:
            continue

        lowered = text.lower()

        if element.name in ["h2", "h3"]:
            summary_lines.append(f"**{text}**")
        elif any(keyword in lowered for keyword in important_keywords):
            summary_lines.append(text)

        if len(summary_lines) >= max_items:
            break

    if not summary_lines:
        raw_text = clean_text(soup.get_text(" ", strip=True))
        fallback_sentences = re.split(r"(?<=[.!?])\s+", raw_text)
        summary_lines = [sentence for sentence in fallback_sentences if len(sentence) > 30][:max_items]

    if not summary_lines:
        return "No readable patch note summary was available."

    bullet_summary = "\n".join(f"• {line[:240]}" for line in summary_lines)

    return bullet_summary[:1000]

async def get_latest_arena_patch() -> dict:
    # First try the structured Zendesk Help Center API.
    try:
        api_url = (
            f"{ARENA_PATCH_NOTES_API_URL}"
            "?sort_by=updated_at&sort_order=desc&per_page=10"
        )

        data = await fetch_json(api_url)
        articles = data.get("articles", [])

        patch_articles = [
            article
            for article in articles
            if article.get("title", "").startswith("Patch Notes")
        ]

        if patch_articles:
            latest_article = patch_articles[0]

            summary = summarize_article_body(latest_article.get("body", ""))
            return {
                "title": latest_article["title"],
                "url": latest_article["html_url"],
                "note": "Latest MTG Arena patch note found automatically through the Help Center API.",
                "summary": summary,
            }
    except Exception as error:
        print(f"Arena API fetch failed: {error}")

    # If API fails, try the regular page.
    try:
        html = await fetch_html(ARENA_PATCH_NOTES_URL)
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.find_all("a", href=True):
            title = link.get_text(" ", strip=True)

            if title.startswith("Patch Notes"):
                href = link["href"]

                if href.startswith("/"):
                    href = "https://mtgarena-support.wizards.com" + href

                return {
                    "title": title,
                    "url": href,
                    "note": "Latest MTG Arena patch note found automatically from the official Wizards support page.",
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
        "note": "Could not detect the latest patch automatically, so here is the official patch notes page.",
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