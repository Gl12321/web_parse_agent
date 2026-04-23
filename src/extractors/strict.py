from typing import Dict, Any, Type, List
from pydantic import BaseModel

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.logger import setup_logger

logger = setup_logger("STRICT_EXTRACTOR")


class StrictExtractor:
    def __init__(self, llm: BaseChatModel, chunk_size: int = 4000):
        self.llm = llm
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=500,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def extract(self, markdown: str, goal: str, schema: Type[BaseModel]) -> List[Dict[str, Any]]:
        if not markdown or not markdown.strip():
            return [schema().model_dump()]

        chunks = self.text_splitter.split_text(markdown)
        logger.info(f"Strict extraction: {len(chunks)} chunk(s) for schema {schema.__name__}")

        results = []
        for i, chunk in enumerate(chunks):
            result = self._extract_chunk(chunk, goal, schema, chunk_index=i)
            if result and not result.get("_extraction_error"):
                results.append(result)

        return results if results else [schema().model_dump()]

    def _extract_chunk(self, chunk: str, goal: str, schema: Type[BaseModel], chunk_index: int = 0) -> Dict[str, Any]:
        import json

        schema_json = schema.model_json_schema()

        prompt = f"""Extract information about: {goal}

            From content:
            ---
            {chunk}
            ---
            
            You MUST return a JSON object matching this exact schema:
            {json.dumps(schema_json, indent=2)}
            
            Rules:
            - Follow schema structure exactly
            - Use null for missing fields
            - Use [] for empty list fields
            - No extra fields not in schema"""

        system_prompt = """You are a data extraction specialist.
            Extract data according to the provided JSON schema.
            Return ONLY valid JSON matching the schema exactly."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            content = self._clean_json(response.content)

            parsed = schema.model_validate_json(content)
            logger.info(f"Chunk {chunk_index}: strict extraction OK")
            return parsed.model_dump()

        except Exception as e:
            logger.error(f"Chunk {chunk_index}: extraction failed: {e}")
            return schema().model_dump()

    def _clean_json(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
