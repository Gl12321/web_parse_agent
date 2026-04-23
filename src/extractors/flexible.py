from typing import Dict, Any, List, Optional
import json

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.logger import setup_logger

logger = setup_logger("FLEXIBLE_EXTRACTOR")


class FlexibleExtractor:
    def __init__(self, llm: BaseChatModel, chunk_size: int = 4000):
        self.llm = llm
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=500,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.system_prompt = """You are a data extraction specialist.
            Extract all relevant information from the provided content.
            Return ONLY a valid JSON object. No explanations, no markdown code blocks, just pure JSON.
            If no relevant information is found, return an empty object: {}"""

    def extract(self, markdown: str, goal: str) -> List[Dict[str, Any]]:
        if not markdown or not markdown.strip():
            return [{}]

        chunks = self.text_splitter.split_text(markdown)
        logger.info(f"Processing {len(chunks)} chunk(s) for goal: {goal}")

        results = []
        for i, chunk in enumerate(chunks):
            result = self._extract_chunk(chunk, goal, chunk_index=i)
            if result and not result.get("_extraction_error"):
                results.append(result)

        return results if results else [{}]

    def _extract_chunk(self, chunk: str, goal: str, chunk_index: int = 0) -> Dict[str, Any]:
        prompt = f"""Goal: {goal}
            Extract relevant information from:
            ---
            {chunk}
            ---
            
            Return JSON object with extracted data."""

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            content = self._clean_json(response.content)

            if not content or content == "{}":
                return {}

            return json.loads(content)

        except json.JSONDecodeError as e:
            logger.error(f"Chunk {chunk_index}: JSON parse failed: {e}")
            return {"_extraction_error": "json_parse_failed", "_chunk": chunk_index}
        except Exception as e:
            logger.error(f"Chunk {chunk_index}: extraction failed: {e}")
            return {"_extraction_error": str(e), "_chunk": chunk_index}

    def _clean_json(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
