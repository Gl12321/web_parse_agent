from typing import List, Optional

from langchain_core.messages import SystemMessage, HumanMessage

from src.agent.nodes.base import BaseAgent
from src.core.logger import setup_logger

logger = setup_logger("NAVIGATOR_AGENT")


class NavigatorAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(llm)
        self.system_prompt = "You are a URL selection specialist. Be STRICT: only pick URLs directly relevant to the goal. Return NONE if no relevant URLs exist."

    def select_next_url(self, candidates: List[str], goal: str) -> Optional[str]:
        if not candidates:
            logger.info("Navigator: no candidates, returning None")
            return None
        if len(candidates) == 1:
            logger.info(f"Navigator: single candidate, returning {candidates[0]}")
            return candidates[0]
        result = self._llm_select(candidates, goal)
        logger.info(f"Navigator: LLM selected {result}")
        return result

    def _llm_select(self, candidates: List[str], goal: str) -> Optional[str]:
        prompt = f"""Goal: {goal}
            
            Available URLs:
            {chr(10).join(f"- {url}" for url in candidates)}
            
            STRICT RULES:
            1. Only select URL if it DIRECTLY helps achieve the goal
            2. Ignore URLs that are generic (home, about, contact, etc.) unless goal specifically asks for them
            3. If NO URL is relevant to the goal: return exactly "NONE"
            
            Response: single URL or "NONE" """

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            selected = response.content.strip()

            selected = selected.split('\n')[0].strip()
            selected = selected.strip('"\'<>[]')

            if selected.upper() == "NONE":
                logger.info("No relevant URLs found")
                return None

            if selected in candidates:
                logger.info(f"Selected: {selected}")
                return selected

            for cand in candidates:
                if selected in cand or cand in selected:
                    logger.info(f"Matched: {cand}")
                    return cand

            return candidates[0]

        except Exception as e:
            logger.error(f"Selection failed: {e}")
            return candidates[0]
