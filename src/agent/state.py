from typing import Optional, Type, List, Dict
from pydantic import BaseModel
from typing import TypedDict

class AgentState(TypedDict):
    start_url: str
    goal: str # info for prompt
    mode: str # strict or flexible
    schema: Optional[Type[BaseModel]] # pydantic schema

    to_visit: List[str]
    current_depth: int

    pages_raw: Dict[str, str] # url -> markdown

    chunks: Dict[str, List[str]]       # url -> [chunk1, chunk2, ...]
    chunks_extracted: Dict[str, List[Dict]]  # url -> [json1, json2, ...]

    page_results: Dict[str, Dict]      # url -> агрегированный JSON по странице

    final_result: Optional[Dict]       # Итоговый JSON после агрегации всех страниц

    #контроль
    max_depth: int
    max_pages: int
    max_chunk_size: int
    pages_processed: int
    done: bool
