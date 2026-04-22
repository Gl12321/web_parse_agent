from typing import Dict, Any, List

from src.core.config import get_settings
from src.core.logger import setup_logger
from src.infrastructure.llm.llm_wrapper import get_llm

settings = get_settings()
logger = setup_logger("BASE_AGENT")


class BaseAgent:
    def __init__(self, model_key: str = "default"):
        cfg = settings.MODELS.get(model_key, settings.MODELS["default"])
        self.llm = get_llm(model_key)
        self.system_prompt = ""
        self.model_key = model_key
        logger.info(f"Initialized {self.__class__.__name__} with model: {cfg.get('model_name', 'unknown')}")

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