import os
from typing import Optional, List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from dataclasses import dataclass
import asyncio
import html2text


os.environ.setdefault(
    'PLAYWRIGHT_BROWSERS_PATH',
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ms-playwright')
)


@dataclass
class PageData:
    url: str
    markdown: str
    title: str
    links: List[str]


class Crawl4AIAdapter:
    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[str] = None
    ):
        self.browser_config = BrowserConfig(
            headless=headless,
            verbose=False
        )

        if proxy:
            self.browser_config.proxy = proxy

        self.crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            markdown_generator=None,
            page_timeout=60000
        )

        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = True
        self.h2t.body_width = 0

    def fetch(self, url: str) -> Optional[PageData]:
        return asyncio.run(self._async_fetch(url))

    async def _async_fetch(self, url: str) -> Optional[PageData]:
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.crawler_config)

            html = result.html or ""
            markdown = self.h2t.handle(html)

            links = []
            if result.links and 'internal' in result.links:
                links = [link['href'] for link in result.links['internal'] if 'href' in link]

            return PageData(
                url=url,
                markdown=markdown,
                title=result.metadata.get('title', '') if result.metadata else '',
                links=links
            )


if __name__ == "__main__":
    url = ""

    crawler = Crawl4AIAdapter()
    page = crawler.fetch(url)

    if page:
        print(f"url: {page.url}")
        print(f"title: {page.title}")
        print(f"links: {len(page.links)}")
        print(f"amount chars: {len(page.markdown)}")
        print("\nMARKDOWN\n")
        print(page.markdown)