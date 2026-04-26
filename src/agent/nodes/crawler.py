from typing import Optional

from src.agent.nodes.base import BaseAgent
from src.infrastructure.crawler import Crawl4AIAdapter, PageData
from src.core.logger import setup_logger

logger = setup_logger("CRAWLER_AGENT")


class CrawlerAgent(BaseAgent):
    def __init__(self):
        self.crawler = Crawl4AIAdapter()

    def fetch(self, url: str) -> Optional[PageData]:
        try:
            logger.info(f"Fetching: {url}")
            result = self.crawler.fetch(url)
            if result:
                logger.info(f"Success: {url} ({len(result.markdown)} chars, {len(result.links)} links)")
            else:
                logger.warning(f"Empty result: {url}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
