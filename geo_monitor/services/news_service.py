from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from geo_monitor.models.geo import Geo
from geo_monitor.models.news import News
from geo_monitor.utils.rss_parser import fetch_rss_entries


class NewsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_and_store(self, geo: Geo, days_back: int = 7) -> list[News]:
        saved_news = []

        for feed_url in geo.rss_feeds:
            entries = await fetch_rss_entries(feed_url, days_back)

            for entry in entries:
                url = entry.get("url")

                if not url:
                    continue

                existing = await self.db.scalar(
                    select(News).where(News.url == url)
                )

                if existing:
                    continue

                news = News(
                    geo_id=geo.id,
                    title=entry.get("title", ""),
                    url=url,
                    source=entry.get("source", "Google News"),
                    source_type="google_news",
                    published_at=entry.get("published_at"),
                    raw_content=entry.get("content", ""),
                )

                self.db.add(news)
                saved_news.append(news)

        await self.db.commit()

        return saved_news

    async def get_latest(self, geo_id: int, limit: int = 20) -> list[News]:
        result = await self.db.execute(
            select(News)
            .where(News.geo_id == geo_id)
            .order_by(News.published_at.desc())
            .limit(limit)
        )

        return list(result.scalars().all())