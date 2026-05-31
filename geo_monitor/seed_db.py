import asyncio
import geo_monitor.models

from sqlalchemy import select

from geo_monitor.database import AsyncSessionLocal
from geo_monitor.models.geo import Geo


async def main():
    async with AsyncSessionLocal() as db:
        existing = await db.scalar(select(Geo).where(Geo.code == "DE"))

        if existing:
            print("GEO Germany already exists")
            return

        geo = Geo(
            code="DE",
            name="Germany",
            language="de",
            rss_feeds=[
                "https://news.google.com/rss/search?q=Germany&hl=en&gl=US&ceid=US:en"
            ],
            is_active=True,
        )

        db.add(geo)
        await db.commit()

        print("GEO Germany added successfully")


if __name__ == "__main__":
    asyncio.run(main())