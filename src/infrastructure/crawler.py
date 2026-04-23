from typing import Optional, List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from dataclasses import dataclass
import asyncio


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
        use_stealth: bool = True,
        proxy: Optional[str] = None,
        wait_for: Optional[str] = None
    ):
        extra_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
        ] if use_stealth else []

        self.browser_config = BrowserConfig(
            headless=headless,
            verbose=False,
            extra_args=extra_args,
            user_agent_mode='random' if use_stealth else None
        )

        self.crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            markdown_generator=DefaultMarkdownGenerator(),
            exclude_external_links=True,
            exclude_social_media_links=True,
            wait_for=wait_for,
            page_timeout=60000
        )

        if proxy:
            self.browser_config.proxy = proxy

    def fetch(self, url: str) -> Optional[PageData]:
        return asyncio.run(self._async_fetch(url))

    async def _async_fetch(self, url: str) -> Optional[PageData]:
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.crawler_config)

            links = []
            if result.links and 'internal' in result.links:
                links = [link['href'] for link in result.links['internal'] if 'href' in link]

            return PageData(
                url=url,
                markdown=result.markdown,
                title=result.metadata.get('title', '') if result.metadata else '',
                links=links
            )


if __name__ == "__main__":
    url = "https://innowise.com/contact-us/"

    crawler = Crawl4AIAdapter()
    page = crawler.fetch(url)

    if page:
        print(f"URL: {page.url}")
        print(f"Title: {page.title}")
        print(f"Links: {len(page.links)}")
        print(f"\n--- MARKDOWN ---\n")
        print(page.markdown[:21000])
        if len(page.markdown) > 2000:
            print(f"\n... [{len(page.markdown) - 2000} chars more]")



