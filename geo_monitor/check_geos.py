import asyncio
import geo_monitor.models

from sqlalchemy import select
from geo_monitor.database import AsyncSessionLocal
from geo_monitor.models.geo import Geo


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Geo))
        geos = result.scalars().all()

        for geo in geos:
            print(geo.id, geo.code, geo.name, geo.rss_feeds)


if __name__ == "__main__":
    asyncio.run(main())