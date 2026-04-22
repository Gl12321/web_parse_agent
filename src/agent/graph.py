import asyncio
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

from langgraph.graph import StateGraph, END

from src.agent.state import AgentState
from src.infrastructure.crawler import Crawl4AIAdapter, PageData


class WebParsingGraph:
    def __init__(
        self,
        navigator=None,
        extractor=None,
        aggregator=None,
        crawler: Optional[Crawl4AIAdapter] = None,
        max_depth: int = 3,
        max_pages: int = 10
    ):
        self.navigator = navigator
        self.extractor = extractor
        self.aggregator = aggregator
        self.crawler = crawler or Crawl4AIAdapter(use_stealth=True)
        self.max_depth = max_depth
        self.max_pages = max_pages

    def _init_state(self, state: AgentState) -> AgentState:
        if not state.get("to_visit"):
            state["to_visit"] = [state["start_url"]]
        if state.get("current_depth") is None:
            state["current_depth"] = 0
        if state.get("pages_processed") is None:
            state["pages_processed"] = 0
        if state.get("done") is None:
            state["done"] = False
        if state.get("pages_raw") is None:
            state["pages_raw"] = {}
        if state.get("page_results") is None:
            state["page_results"] = {}
        if state.get("current_url") is None:
            state["current_url"] = None
        return state

    def _navigator(self, state: AgentState) -> AgentState:
        to_visit = state.get("to_visit", [])
        if not to_visit:
            state["done"] = True
            state["current_url"] = None
            return state

        if self.navigator:
            next_url = self.navigator.select_next_url(
                candidates=to_visit,
                goal=state["goal"],
                current_depth=state.get("current_depth", 0)
            )
        else:
            next_url = to_visit[0]

        state["to_visit"] = [u for u in to_visit if u != next_url]
        state["current_url"] = next_url
        return state

    async def _crawler(self, state: AgentState) -> AgentState:
        url = state.get("current_url")
        if not url:
            return state

        try:
            page_data: Optional[PageData] = await self.crawler.fetch(url)
            if page_data:
                state["pages_raw"][url] = page_data.markdown
                state["_current_links"] = page_data.links
            else:
                state["pages_raw"][url] = ""
                state["_current_links"] = []
        except Exception:
            state["pages_raw"][url] = ""
            state["_current_links"] = []

        state["pages_processed"] = state.get("pages_processed", 0) + 1
        return state

    def _extractor(self, state: AgentState) -> AgentState:
        url = state.get("current_url")
        if not url:
            return state

        markdown = state["pages_raw"].get(url, "")
        if not markdown:
            state["page_results"][url] = {}
            return state

        if self.extractor:
            result = self.extractor.extract(
                markdown=markdown,
                goal=state["goal"],
                mode=state.get("mode", "flexible"),
                schema=state.get("schema")
            )
        else:
            result = {}

        state["page_results"][url] = result

        new_links = state.get("_current_links", [])
        to_visit = state.get("to_visit", [])
        visited = set(state["pages_raw"].keys())

        for link in new_links:
            full_url = self._normalize_url(url, link)
            if full_url and full_url not in visited and full_url not in to_visit:
                to_visit.append(full_url)

        state["to_visit"] = to_visit
        state["current_depth"] = state.get("current_depth", 0) + 1
        return state

    def _normalize_url(self, base: str, href: str) -> Optional[str]:
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            return None
        full = urljoin(base, href)
        parsed = urlparse(full)
        base_domain = urlparse(base).netloc
        if parsed.netloc and parsed.netloc != base_domain:
            return None
        return full.split("#")[0]

    def _should_continue(self, state: AgentState) -> str:
        to_visit = state.get("to_visit", [])
        depth = state.get("current_depth", 0)
        pages = state.get("pages_processed", 0)
        max_depth = state.get("max_depth", self.max_depth)
        max_pages = state.get("max_pages", self.max_pages)

        if not to_visit or depth >= max_depth or pages >= max_pages:
            return "aggregate"
        return "continue"

    def _aggregator(self, state: AgentState) -> AgentState:
        page_results = state.get("page_results", {})

        if not page_results:
            state["final_result"] = {}
            return state

        if self.aggregator:
            final = self.aggregator.aggregate(
                page_results=page_results,
                goal=state["goal"]
            )
        else:
            final = self._fallback_aggregate(page_results)

        state["final_result"] = final
        return state

    def _fallback_aggregate(self, page_results: Dict) -> Dict:
        merged = {}
        for result in page_results.values():
            if isinstance(result, dict):
                for key, value in result.items():
                    if key in merged:
                        if isinstance(merged[key], list):
                            if value not in merged[key]:
                                merged[key].append(value)
                        elif merged[key] != value:
                            merged[key] = [merged[key], value]
                    else:
                        merged[key] = value
        return merged

    def _build_sync_workflow(self):
        workflow = StateGraph(AgentState)

        def sync_crawler(state):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop:
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self._crawler(state))
            else:
                return asyncio.run(self._crawler(state))

        workflow.add_node("init", self._init_state)
        workflow.add_node("navigator", self._navigator)
        workflow.add_node("crawler", sync_crawler)
        workflow.add_node("extractor", self._extractor)
        workflow.add_node("aggregator", self._aggregator)

        workflow.set_entry_point("init")
        workflow.add_edge("init", "navigator")
        workflow.add_edge("navigator", "crawler")
        workflow.add_edge("crawler", "extractor")
        workflow.add_conditional_edges(
            "extractor",
            self._should_continue,
            {"continue": "navigator", "aggregate": "aggregator"}
        )
        workflow.add_edge("aggregator", END)

        return workflow.compile()

    async def run(
        self,
        start_url: str,
        goal: str,
        mode: str = "flexible",
        schema=None
    ) -> Dict[str, Any]:
        initial_state: AgentState = {
            "start_url": start_url,
            "goal": goal,
            "mode": mode,
            "schema": schema,
            "to_visit": [start_url],
            "current_depth": 0,
            "pages_raw": {},
            "page_results": {},
            "final_result": None,
            "max_depth": self.max_depth,
            "max_pages": self.max_pages,
            "max_chunk_size": 8000,
            "pages_processed": 0,
            "done": False,
            "current_url": None,
            "chunks": {},
            "chunks_extracted": {},
        }

        workflow = self._build_sync_workflow()
        result = await workflow.ainvoke(initial_state)
        return result.get("final_result", {})
