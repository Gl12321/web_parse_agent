from typing import Optional, Type
from pydantic import BaseModel

from src.infrastructure.llm.llm_wrapper import get_llm
from src.agent.agents.base import BaseAgent
from src.agent.agents.extractor_agent import ExtractorAgent
from src.agent.agents.navigator_agent import NavigatorAgent
from src.agent.agents.aggregator_agent import AggregatorAgent
from src.agent.agents.crawler_agent import CrawlerAgent
from src.agent.graph import WebParsingGraph
from src.extractors.schemas.contact import ContactInfo


def run_parser(
        url: str,
        goal: str,
        mode: str = "flexible",
        schema: Optional[Type[BaseModel]] = None,
        max_depth: int = 2,
        max_pages: int = 5
) -> dict:

    llm = get_llm()
    navigator = NavigatorAgent(llm)
    extractor = ExtractorAgent(llm)
    aggregator = AggregatorAgent(llm)
    crawler = CrawlerAgent()

    graph = WebParsingGraph(
        navigator=navigator,
        extractor=extractor,
        aggregator=aggregator,
        crawler=crawler,
        max_depth=max_depth,
        max_pages=max_pages
    )

    print(f"Starting crawl {url}")
    print(f"Goal {goal}")
    print(f"Mode {mode} Max depth {max_depth} Max pages {max_pages}")

    result = graph.run(
        start_url=url,
        goal=goal,
        mode=mode,
        schema=schema
    )

    print(f"Pages processed: {result['pages_processed']}")
    print(f"Visited: {result['visited_urls']}")
    print(f"Remaining in queue: {len(result['to_visit'])}")

    return result


def main():
    print("=" * 60)
    print("EXAMPLE 1 Flexible extraction")
    print("=" * 60)

    url = "https://jet.su"

    result = run_parser(
        url=url,
        goal="Extract all contact information including emails, phone numbers, and addresses",
        mode="flexible",
        max_depth=3,
        max_pages=10
    )

    print("\nFinal result:")
    import json
    print(json.dumps(result['final_result']))

    print("EXAMPLE 2 Strict extraction with Pydantic schema")

    result = run_parser(
        url=url,
        goal="Extract contact information",
        mode="strict",
        schema=ContactInfo,
        max_depth=3,
        max_pages=10
    )

    print("\nFinal result")
    print(json.dumps(result['final_result']))


if __name__ == "__main__":
    main()
