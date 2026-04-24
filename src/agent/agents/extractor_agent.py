from typing import Dict, Any, Optional, Type, List
from pydantic import BaseModel

from src.agent.agents.base import BaseAgent
from src.extractors.flexible import FlexibleExtractor
from src.extractors.strict import StrictExtractor
from src.core.logger import setup_logger

logger = setup_logger("EXTRACTOR_AGENT")


class ExtractorAgent(BaseAgent):
    def __init__(self, llm=None, chunk_size: int = 8000):
        super().__init__(llm)
        self.flexible_extractor = FlexibleExtractor(self.llm, chunk_size)
        self.strict_extractor = StrictExtractor(self.llm, chunk_size)

    def extract(
        self,
        markdown: str,
        goal: str,
        mode: str = "flexible",
        schema: Optional[Type[BaseModel]] = None
    ) -> List[Dict[str, Any]]:
        if not markdown or not markdown.strip():
            if schema:
                return [schema().model_dump()]
            return [{}]

        if mode == "strict" and schema is not None:
            return self.strict_extractor.extract(markdown, goal, schema)
        else:
            return self.flexible_extractor.extract(markdown, goal)
