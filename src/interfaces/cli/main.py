import os
import sys
from typing import Optional, Type
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.crawler import Crawl4AIAdapter
from src.agent.agents import NavigatorAgent, ExtractorAgent, AggregatorAgent
from src.agent.graph import WebParsingGraph


class ContactInfo(BaseModel):
    emails: list[str] = []
    phones: list[str] = []
    addresses: list[str] = []


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
    crawler = Crawl4AIAdapter(llm)

    graph = WebParsingGraph(
        navigator=navigator,
        extractor=extractor,
        aggregator=aggregator,
        crawler=crawler,
        max_depth=max_depth,
        max_pages=max_pages
    )

    print(f"Starting crawl: {url}")
    print(f"Goal: {goal}")
    print(f"Mode: {mode}, Max depth: {max_depth}, Max pages: {max_pages}")
    print("-" * 50)

    result = graph.run(
        start_url=url,
        goal=goal,
        mode=mode,
        schema=schema
    )

    print("-" * 50)
    print(f"Pages processed: {result['pages_processed']}")
    print(f"Visited: {result['visited_urls']}")
    print(f"Remaining in queue: {len(result['to_visit'])}")

    return result


def main():
    print("=" * 60)
    print("EXAMPLE 1: Flexible extraction")
    print("=" * 60)

    url = "https://jet.su/about/contacts/"

    result = run_parser(
        url=url,
        goal="Extract all contact information including emails, phone numbers, and addresses",
        mode="flexible",
        max_depth=1,
        max_pages=3
    )

    print("\nFinal result:")
    import json
    print(json.dumps(result['final_result'], indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("EXAMPLE 2: Strict extraction with Pydantic schema")
    print("=" * 60)

    result = run_parser(
        url=url,
        goal="Extract contact information",
        mode="strict",
        schema=ContactInfo,
        max_depth=1,
        max_pages=3
    )

    print("\nFinal result:")
    print(json.dumps(result['final_result'], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
