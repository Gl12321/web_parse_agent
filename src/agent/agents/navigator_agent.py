from typing import Dict, Any, List, Optional

from langchain_core.messages import SystemMessage, HumanMessage

from src.agent.agents.base import BaseAgent
from src.core.logger import setup_logger

logger = setup_logger("NAVIGATOR_AGENT")


class NavigatorAgent(BaseAgent):
    def __init__(self, model_key: str = "navigator"):
        super().__init__(model_key)
        self.system_prompt = "You are a URL selection specialist. Pick the most relevant URL."

    def select_next_url(self, candidates: List[str], goal: str, current_depth: int = 0) -> Optional[str]:
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]

        return self._llm_select(candidates, goal)

    def _llm_select(self, candidates: List[str], goal: str) -> Optional[str]:
        prompt = f"""Goal: {goal}        
            Available URLs:
            {chr(10).join(f"- {url}" for url in candidates)}
            
            Return ONLY the single most relevant URL that best matches the goal.
            No explanations, just the URL."""

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            selected = response.content.strip()

            selected = selected.split('\n')[0].strip()
            selected = selected.strip('"\'<>[]')

            if selected in candidates:
                logger.info(f"LLM selected: {selected}")
                return selected

            for cand in candidates:
                if selected in cand or cand in selected:
                    logger.info(f"Matched: {cand}")
                    return cand

            return candidates[0]

        except Exception as e:
            logger.error(f"LLM selection failed: {e}")
            return candidates[0]
