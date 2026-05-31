import asyncio

from geo_monitor.services.ai_service import AIService


async def main():
    ai = AIService()

    result = await ai.analyze_news(
        "Germany pushes back on US attack over streaming law"
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())