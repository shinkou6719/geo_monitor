import asyncio

from geo_monitor.utils.rss_parser import fetch_rss_entries


async def main():
    url = "https://news.google.com/rss/search?q=Germany&hl=en&gl=US&ceid=US:en"
    news = await fetch_rss_entries(url)

    print(f"Получено новостей: {len(news)}")

    for item in news[:5]:
        print()
        print("TITLE:", item["title"])
        print("URL:", item["url"])
        print("SOURCE:", item["source"])
        print("DATE:", item["published_at"])


if __name__ == "__main__":
    asyncio.run(main())