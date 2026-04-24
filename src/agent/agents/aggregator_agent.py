from typing import Dict, Any, List, Type, Optional
import json

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from src.agent.agents.base import BaseAgent
from src.core.logger import setup_logger

logger = setup_logger("AGGREGATOR_AGENT")


class AggregatorAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(llm)
        self.system_prompt = "You are a data aggregation specialist. Merge and deduplicate data."

    def aggregate_flexible(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info(f"Aggregate flexible: {len(data)} items")
        if not data:
            return {}
        if len(data) == 1:
            logger.info("Aggregate flexible: single item, no aggregation needed")
            return data[0]
        return self._llm_aggregate(data, schema=None)

    def aggregate_strict(self, data: List[Dict[str, Any]], schema: Type[BaseModel]) -> Dict[str, Any]:
        logger.info(f"Aggregate strict: {len(data)} items for schema {schema.__name__}")
        if not data:
            return schema().model_dump()
        if len(data) == 1:
            try:
                result = schema.model_validate(data[0]).model_dump()
                logger.info("Aggregate strict: single item, no aggregation needed")
                return result
            except:
                return data[0]

        result = self._llm_aggregate(data, schema=schema)

        try:
            return schema.model_validate(result).model_dump()
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            result["_schema_validation_error"] = True
            return result

    def _llm_aggregate(self, data: List[Dict[str, Any]], schema: Optional[Type[BaseModel]] = None) -> Dict[str, Any]:
        data_json = json.dumps(data, ensure_ascii=False, indent=2)

        prompt = f"""Merge and deduplicate the following JSON data:
        
            {data_json}
            
            Instructions:
            1. Merge all objects into one
            2. For duplicate keys with different values, combine into arrays
            3. Remove duplicate values in arrays
            4. Return only valid JSON, no markdown"""

        if schema:
            schema_json = schema.model_json_schema()
            prompt += f"""
                You MUST follow this schema exactly:
                {json.dumps(schema_json, indent=2)}
                
                - Only fields from the schema
                - No extra fields
                - Use null for missing data"""

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            content = self._clean_json(response.content)

            return json.loads(content)

        except Exception as e:
            logger.error(f"LLM aggregation failed: {e}")
            return self._simple_merge(data)

    def _clean_json(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()

    def _simple_merge(self, data: List[Dict]) -> Dict:
        merged = {}
        for item in data:
            for key, value in item.items():
                if key not in merged:
                    merged[key] = value
                elif isinstance(merged[key], list) and isinstance(value, list):
                    seen = set(str(x) for x in merged[key])
                    for v in value:
                        if str(v) not in seen:
                            merged[key].append(v)
                elif merged[key] != value:
                    if not isinstance(merged[key], list):
                        merged[key] = [merged[key]]
                    if value not in merged[key]:
                        merged[key].append(value)
        return merged
