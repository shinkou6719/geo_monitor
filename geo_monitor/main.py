import asyncio

from geo_monitor.services.bot_service import start_bot


async def main():
    print("Bot started")
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())