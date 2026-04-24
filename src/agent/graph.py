from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse

from langgraph.graph import StateGraph, END

from src.agent.state import AgentState
from src.infrastructure.crawler import PageData


class WebParsingGraph:
    def __init__(
        self,
        navigator=None,
        extractor=None,
        aggregator=None,
        crawler=None,
        max_depth: int = 3,
        max_pages: int = 10
    ):
        self.navigator = navigator
        self.extractor = extractor
        self.aggregator = aggregator
        self.crawler = crawler
        self.max_depth = max_depth
        self.max_pages = max_pages
        self._workflow = self._build_workflow()

    def _navigator_node(self, state: AgentState) -> AgentState:
        to_visit = state.get("to_visit", [])

        to_visit = [(u, d) for u, d in to_visit if d <= self.max_depth]
        state["to_visit"] = to_visit
        
        if not to_visit:
            state["done"] = True
            state["current_url"] = None
            state["current_depth"] = 0
            return state

        candidates = [u for u, _ in to_visit]

        next_url = self.navigator.select_next_url(candidates, state["goal"])

        if next_url is None:
            state["done"] = True
            state["current_url"] = None
            state["current_depth"] = 0
        else:
            selected_depth = next((d for u, d in to_visit if u == next_url), 0)
            state["to_visit"] = [(u, d) for u, d in to_visit if u != next_url]
            state["current_url"] = next_url
            state["current_depth"] = selected_depth

        return state

    def _crawler_node(self, state: AgentState) -> AgentState:
        url = state.get("current_url")
        if not url:
            return state

        try:
            page_data: Optional[PageData] = self.crawler.fetch(url)
            if page_data:
                state["pages_raw"][url] = page_data.markdown
                state["_current_links"] = page_data.links
            else:
                state["pages_raw"][url] = ""
                state["_current_links"] = []
        except Exception as e:
            state["pages_raw"][url] = ""
            state["_current_links"] = []

        state["pages_processed"] = state.get("pages_processed", 0) + 1
        return state

    def _extractor_node(self, state: AgentState) -> AgentState:
        url = state.get("current_url")
        if not url:
            return state

        markdown = state["pages_raw"].get(url, "")
        if not markdown:
            state["chunks_extracted"][url] = [{}]
            return state

        chunk_results = self.extractor.extract(
            markdown=markdown,
            goal=state["goal"],
            mode=state.get("mode", "flexible"),
            schema=state.get("schema")
        )
        state["chunks_extracted"][url] = chunk_results
        return state

    def _page_aggregator_node(self, state: AgentState) -> AgentState:
        url = state.get("current_url")
        if not url:
            return state

        chunk_results = state["chunks_extracted"].get(url, [])
        if not chunk_results:
            state["page_results"][url] = {}
        else:
            schema = state.get("schema")
            if schema:
                page_result = self.aggregator.aggregate_strict(chunk_results, schema)
            else:
                page_result = self.aggregator.aggregate_flexible(chunk_results)
            state["page_results"][url] = page_result

        new_links = state.get("_current_links", [])
        to_visit: List[Tuple[str, int]] = state.get("to_visit", [])
        visited = set(state["pages_raw"].keys())
        current_depth = state.get("current_depth", 0)
        next_depth = current_depth + 1

        for link in new_links:
            full_url = self._normalize_url(url, link)
            if full_url and full_url not in visited:
                if not any(u == full_url for u, _ in to_visit):
                    to_visit.append((full_url, next_depth))

        state["to_visit"] = to_visit
        return state

    def _normalize_url(self, base: str, href: str) -> Optional[str]:
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            return None
        full = urljoin(base, href)
        parsed = urlparse(full)
        base_domain = urlparse(base).netloc

        if parsed.netloc and parsed.netloc != base_domain:
            return None

        skip_ext = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.css',
                    '.js', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.avi')
        path_lower = parsed.path.lower()
        if any(path_lower.endswith(ext) for ext in skip_ext):
            return None

        return full.split("#")[0]

    def _should_continue(self, state: AgentState) -> str:
        to_visit = state.get("to_visit", [])
        pages = state.get("pages_processed", 0)

        if not to_visit or pages >= self.max_pages:
            return "final"
        
        return "continue"

    def _final_aggregator_node(self, state: AgentState) -> AgentState:
        page_results = state.get("page_results", {})

        if not page_results:
            state["final_result"] = {}
            return state

        all_data: List[Dict] = list(page_results.values())

        schema = state.get("schema")
        if schema:
            final = self.aggregator.aggregate_strict(all_data, schema)
        else:
            final = self.aggregator.aggregate_flexible(all_data)

        state["final_result"] = final
        return state

    def _build_workflow(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("navigator", self._navigator_node)
        workflow.add_node("crawler", self._crawler_node)
        workflow.add_node("extractor", self._extractor_node)
        workflow.add_node("page_aggregator", self._page_aggregator_node)
        workflow.add_node("final_aggregator", self._final_aggregator_node)

        workflow.set_entry_point("navigator")
        
        workflow.add_conditional_edges(
            "navigator",
            lambda state: "crawl" if state.get("current_url") else "final",
            {"crawl": "crawler", "final": "final_aggregator"}
        )
        
        workflow.add_edge("crawler", "extractor")
        workflow.add_edge("extractor", "page_aggregator")
        
        workflow.add_conditional_edges(
            "page_aggregator",
            self._should_continue,
            {"continue": "navigator", "final": "final_aggregator"}
        )
        
        workflow.add_edge("final_aggregator", END)

        return workflow.compile()

    def run(self, start_url: str, goal: str, mode: str = "flexible", schema=None) -> Dict[str, Any]:
        initial_state: AgentState = {
            "start_url": start_url,
            "goal": goal,
            "mode": mode,
            "schema": schema,
            "to_visit": [(start_url, 0)],
            "current_url": None,
            "current_depth": 0,
            "pages_raw": {},
            "_current_links": [],
            "page_results": {},
            "final_result": None,
            "pages_processed": 0,
            "done": False,
            "chunks_extracted": {},
        }

        result = self._workflow.invoke(initial_state)
        return {
            "final_result": result.get("final_result", {}),
            "pages_processed": result.get("pages_processed", 0),
            "visited_urls": list(result.get("pages_raw", {}).keys()),
        }
