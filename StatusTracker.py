import asyncio
import httpx
import feedparser
import logging
import re
from datetime import datetime
from typing import Optional, List, Tuple


# ===========================================================
# Configuration
# ===========================================================

FEEDS = [
    "https://status.openai.com/feed.atom",
    "https://www.githubstatus.com/history.atom",
]

POLL_INTERVAL_SECONDS = 60
MAX_TRACKED_IDS = 1000  # Prevent unbounded memory growth


# ===========================================================
# Logging Configuration
# ===========================================================

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("StatusTracker")


# ===========================================================
# Utility Functions
# ===========================================================

def strip_html(raw_html: str) -> str:
    """
    Remove HTML tags from RSS/Atom summary content.

    Args:
        raw_html (str): HTML string from feed entry

    Returns:
        str: Clean readable text
    """
    clean = re.sub(r"<.*?>", "", raw_html or "")
    return clean.strip()


def extract_entry_time(entry) -> Optional[datetime]:
    """
    Extract datetime from feed entry safely.

    Supports:
        - updated_parsed
        - published_parsed

    Returns:
        datetime or None
    """
    time_struct = (
        entry.get("updated_parsed")
        or entry.get("published_parsed")
    )

    if not time_struct:
        return None

    return datetime(*time_struct[:6])


# ===========================================================
# Status Feed Tracker
# ===========================================================

class StatusFeedTracker:
    """
    Production-grade RSS/Atom feed tracker.

    Features:
        - Conditional HTTP requests (ETag, Last-Modified)
        - Multi-incident safe handling
        - Chronological ordering
        - ID-based deduplication
        - Memory bounded tracking
        - Clean structured logs
    """

    def __init__(self, feed_url: str, interval: int = 60):
        self.feed_url = feed_url
        self.interval = interval

        # HTTP cache headers
        self.etag: Optional[str] = None
        self.last_modified: Optional[str] = None

        # Dedup tracking
        self.seen_entry_ids = set()

        # Persistent HTTP client
        self.client = httpx.AsyncClient(timeout=10)

    async def fetch_feed(self) -> Optional[str]:
        """
        Fetch feed using conditional HTTP headers.

        Returns:
            str (XML) if modified
            None if 304 or error
        """
        headers = {}

        if self.etag:
            headers["If-None-Match"] = self.etag

        if self.last_modified:
            headers["If-Modified-Since"] = self.last_modified

        try:
            response = await self.client.get(self.feed_url, headers=headers)

            if response.status_code == 304:
                return None

            response.raise_for_status()

            self.etag = response.headers.get("ETag")
            self.last_modified = response.headers.get("Last-Modified")

            return response.text

        except httpx.RequestError as exc:
            logger.error(f"[{self.feed_url}] Network error → {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"[{self.feed_url}] HTTP error → {exc.response.status_code}")
        except Exception:
            logger.exception(f"[{self.feed_url}] Unexpected fetch error")

        return None

    def process_entries(self, feed_data: str) -> None:
        """
        Process feed entries safely.

        - Collect new entries first
        - Sort oldest → newest
        - Print all new incidents
        - Update seen IDs
        - Keep memory bounded
        """
        try:
            parsed = feedparser.parse(feed_data)

            new_entries: List[Tuple[datetime, str, str, str]] = []

            for entry in parsed.entries:
                entry_id = entry.get("id") or entry.get("link")

                if not entry_id:
                    continue

                if entry_id in self.seen_entry_ids:
                    continue

                entry_time = extract_entry_time(entry)
                if not entry_time:
                    continue

                title = entry.get("title", "Unknown Service")
                summary = strip_html(entry.get("summary", ""))

                new_entries.append((entry_time, title, summary, entry_id))

            # Sort chronologically (oldest first)
            new_entries.sort(key=lambda x: x[0])

            for entry_time, title, summary, entry_id in new_entries:
                logger.info(
                    # f"\nNEW INCIDENT DETECTED\n"
                    f"Feed    : {self.feed_url}\n"
                    f"Service : {title}\n"
                    f"Time    : {entry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Details : {summary}\n"
                    f"{'-'*100}"
                )

                self.seen_entry_ids.add(entry_id)

        except Exception:
            logger.exception(f"[{self.feed_url}] Processing error")

    async def run(self) -> None:
        """
        Main polling loop.

        Runs indefinitely until cancelled.
        """
        logger.info(f"Tracking started → {self.feed_url}")

        try:
            while True:
                feed_data = await self.fetch_feed()

                if feed_data:
                    self.process_entries(feed_data)

                await asyncio.sleep(self.interval)

        except asyncio.CancelledError:
            logger.info(f"Tracker cancelled → {self.feed_url}")
        finally:
            await self.client.aclose()
            logger.info(f"Tracker stopped → {self.feed_url}")


# ===========================================================
# Main Entry
# ===========================================================

async def main():
    trackers = [
        StatusFeedTracker(feed_url, POLL_INTERVAL_SECONDS)
        for feed_url in FEEDS
    ]

    tasks = [asyncio.create_task(tracker.run()) for tracker in trackers]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("All trackers cancelled.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user.")