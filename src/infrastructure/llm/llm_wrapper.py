from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from src.core.config import get_settings
from src.core.logger import setup_logger

logger = setup_logger("LLM_WRAPPER")


class LLMWrapper:
    _instance: Optional['LLMWrapper'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        settings = get_settings()
        self._llm: Optional[BaseChatModel] = None
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE

        logger.info(f"LLMWrapper initialized with model: {self.model}")

    def get_llm(self) -> BaseChatModel:
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                api_key=get_settings().openai_api_key
            )
            logger.info(f"LLM created: {self.model}")
        return self._llm


_llm_wrapper: Optional[LLMWrapper] = None


def get_llm_wrapper() -> LLMWrapper:
    global _llm_wrapper
    if _llm_wrapper is None:
        _llm_wrapper = LLMWrapper()
    return _llm_wrapper


def get_llm() -> BaseChatModel:
    return get_llm_wrapper().get_llm()
