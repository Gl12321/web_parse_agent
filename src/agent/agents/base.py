from typing import Dict, Any, List, Optional

from langchain_core.language_models import BaseChatModel

from src.infrastructure.llm.llm_wrapper import get_llm
from src.core.logger import setup_logger

logger = setup_logger("BASE_AGENT")


class BaseAgent:
    def __init__(self, llm: Optional[BaseChatModel] = None):
        self.llm = llm
        self.system_prompt = ""
        logger.info(f"Initialized {self.__class__.__name__}")

    def _get_strict_system_prompt(self, context: str) -> str:
        return (
            f"{self.system_prompt}\n"
            f"CONTEXT FROM DATA SOURCES:\n{context}\n\n"
            "STRICT RULES:\n"
            "- No conversational filler (e.g., 'Sure', 'I found').\n"
            "- No abstractions. Use only provided facts and numbers.\n"
            "- If data is missing, state: 'DATA_NOT_FOUND'.\n"
            "- Format: Concise bullet points or direct values."
        )
