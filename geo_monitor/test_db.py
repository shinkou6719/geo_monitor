import asyncio
from geo_monitor.database import engine, Base

from geo_monitor.models.geo import Geo
from geo_monitor.models.news import News
from geo_monitor.models.idea import Idea
from geo_monitor.models.headline import Headline
from geo_monitor.models.report import Report


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("DB tables created successfully")


if __name__ == "__main__":
    asyncio.run(main())