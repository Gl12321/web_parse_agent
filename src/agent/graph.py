from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse

from langgraph.graph import StateGraph, END

from src.agent.state import AgentState
from src.agent.agents.crawler_agent import CrawlerAgent
from src.infrastructure.crawler import PageData
from src.core.logger import setup_logger

logger = setup_logger("GRAPH")


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
        max_depth = state.get("max_depth", self.max_depth)
        to_visit = state.get("to_visit", [])
        
        logger.info(f"Navigator: queue has {len(to_visit)} URLs, max_depth={max_depth}")
        
        to_visit = [(u, d) for u, d in to_visit if d <= max_depth]
        state["to_visit"] = to_visit
        
        if not to_visit:
            logger.info("Navigator: queue empty, done")
            state["done"] = True
            state["current_url"] = None
            state["current_depth"] = 0
            return state

        candidates = [u for u, _ in to_visit]
        logger.info(f"Navigator: {len(candidates)} candidates: {candidates[:3]}...")
        
        next_url = self.navigator.select_next_url(candidates, state["goal"])

        if next_url is None:
            logger.info("Navigator: no URL selected, done")
            state["done"] = True
            state["current_url"] = None
            state["current_depth"] = 0
        else:
            selected_depth = next((d for u, d in to_visit if u == next_url), 0)
            state["to_visit"] = [(u, d) for u, d in to_visit if u != next_url]
            state["current_url"] = next_url
            state["current_depth"] = selected_depth
            logger.info(f"Navigator: selected {next_url} at depth {selected_depth}")
        
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
                logger.info(f"Crawler found {len(page_data.links)} links on {url}")
            else:
                state["pages_raw"][url] = ""
                state["_current_links"] = []
                logger.warning(f"Crawler returned no data for {url}")
        except Exception as e:
            state["pages_raw"][url] = ""
            state["_current_links"] = []
            logger.error(f"Crawler failed for {url}: {e}")

        state["pages_processed"] = state.get("pages_processed", 0) + 1
        return state

    def _extractor_node(self, state: AgentState) -> AgentState:
        url = state.get("current_url")
        if not url:
            return state

        markdown = state["pages_raw"].get(url, "")
        if not markdown:
            state["chunks_extracted"][url] = [{}]
            state["page_results"][url] = {}
            return state

        chunk_results = self.extractor.extract(
            markdown=markdown,
            goal=state["goal"],
            mode=state.get("mode", "flexible"),
            schema=state.get("schema")
        )
        state["chunks_extracted"][url] = chunk_results

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

        added_count = 0
        for link in new_links:
            full_url = self._normalize_url(url, link)
            if full_url and full_url not in visited:
                if not any(u == full_url for u, _ in to_visit):
                    to_visit.append((full_url, next_depth))
                    added_count += 1

        logger.info(f"Extractor: {len(new_links)} raw links, {added_count} added to queue (depth {next_depth})")
        if added_count > 0:
            logger.info(f"Queue now has {len(to_visit)} URLs")

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
        if state.get("done"):
            return "aggregate"
        
        to_visit = state.get("to_visit", [])
        pages = state.get("pages_processed", 0)
        max_pages = state.get("max_pages", self.max_pages)

        if not to_visit or pages >= max_pages:
            return "aggregate"
        
        return "continue"

    def _aggregator_node(self, state: AgentState) -> AgentState:
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
        workflow.add_node("aggregator", self._aggregator_node)

        workflow.set_entry_point("navigator")
        
        workflow.add_conditional_edges(
            "navigator",
            lambda state: "crawl" if state.get("current_url") else "aggregate",
            {"crawl": "crawler", "aggregate": "aggregator"}
        )
        
        workflow.add_edge("crawler", "extractor")
        
        workflow.add_conditional_edges(
            "extractor",
            self._should_continue,
            {"continue": "navigator", "aggregate": "aggregator"}
        )
        
        workflow.add_edge("aggregator", END)

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
            "max_depth": self.max_depth,
            "max_pages": self.max_pages,
            "max_chunk_size": 8000,
            "pages_processed": 0,
            "done": False,
            "chunks_extracted": {},
        }

        result = self._workflow.invoke(initial_state)
        return {
            "final_result": result.get("final_result", {}),
            "pages_processed": result.get("pages_processed", 0),
            "visited_urls": list(result.get("pages_raw", {}).keys()),
            "to_visit": result.get("to_visit", [])
        }
