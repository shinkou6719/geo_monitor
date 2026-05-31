from datetime import datetime
import feedparser


async def fetch_rss_entries(feed_url: str, days_back: int = 7) -> list[dict]:
    feed = feedparser.parse(feed_url)
    entries = []

    for item in feed.entries[:20]:
        published_at = None

        if hasattr(item, "published_parsed") and item.published_parsed:
            published_at = datetime(*item.published_parsed[:6])

        entries.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "source": feed.feed.get("title", "Google News"),
            "published_at": published_at,
            "content": item.get("summary", ""),
        })

    return entries