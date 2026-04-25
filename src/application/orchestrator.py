from typing import Optional, Type, Dict, Any

from src.agent.graph import WebParsingGraph
from src.agent.agents import NavigatorAgent, ExtractorAgent, AggregatorAgent, CrawlerAgent
from src.infrastructure.llm.llm_wrapper import get_llm
from src.infrastructure.database import ExtractionRepository
from pydantic import BaseModel


class ParseOrchestrator:
    def __init__(self, llm=None):
        self.llm = llm if llm else get_llm()
        self.repository = ExtractionRepository()

    def _save_result(self, source_url: str, schema: Type[BaseModel], data: Dict[str, Any]):
        schema_name = schema.__name__

        if schema_name == "ContactInfo":
            self.repository.save_contact_info(source_url, data)
        elif schema_name == "OrganizationInfo":
            self.repository.save_organization_info(source_url, data)
        elif schema_name == "LegalInfo":
            self.repository.save_legal_info(source_url, data)

    def run(
        self,
        url: str,
        goal: str,
        schema: Optional[Type[BaseModel]] = None,
        mode: str = "flexible",
        max_depth: int = 3,
        max_pages: int = 5,
        save_to_db: bool = False
    ) -> Dict[str, Any]:
        graph = WebParsingGraph(
            navigator=NavigatorAgent(llm=self.llm),
            extractor=ExtractorAgent(llm=self.llm),
            aggregator=AggregatorAgent(llm=self.llm),
            crawler=CrawlerAgent(),
            max_depth=max_depth,
            max_pages=max_pages
        )

        result = graph.run(
            start_url=url,
            goal=goal,
            mode=mode,
            schema=schema
        )

        if save_to_db and schema is not None:
            final_result = result.get("final_result", {})
            self._save_result(url, schema, final_result)

        return result
