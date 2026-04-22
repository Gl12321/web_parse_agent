import asyncio
import sys
sys.path.insert(0, '/home/stanislav/web_parse_agent/src')

from src.infrastructure.crawler import Crawl4AIAdapter


async def test():
    url = "https://innowise.com/contact-us/"
    
    crawler = Crawl4AIAdapter()
    page = await crawler.fetch(url)
    
    if page:
        print(f"URL: {page.url}")
        print(f"Title: {page.title}")
        print(f"Links: {len(page.links)}")
        print(f"\n--- MARKDOWN ---\n")
        print(page.markdown[:21000])
        if len(page.markdown) > 2000:
            print(f"\n... [{len(page.markdown) - 2000} chars more]")


if __name__ == "__main__":
    asyncio.run(test())
