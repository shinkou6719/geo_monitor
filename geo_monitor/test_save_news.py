import asyncio
import geo_monitor.models

from sqlalchemy import select

from geo_monitor.database import AsyncSessionLocal
from geo_monitor.models.geo import Geo
from geo_monitor.services.news_service import NewsService


async def main():
    async with AsyncSessionLocal() as db:
        geo = await db.scalar(select(Geo).where(Geo.code == "DE"))

        if not geo:
            print("GEO DE not found")
            return

        service = NewsService(db)
        saved = await service.fetch_and_store(geo)

        print(f"Saved news: {len(saved)}")

        latest = await service.get_latest(geo.id)

        for item in latest[:5]:
            print()
            print(item.id, item.title)
            print(item.url)
            print(item.published_at)


if __name__ == "__main__":
    asyncio.run(main())