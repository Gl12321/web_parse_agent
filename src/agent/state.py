from typing import Optional, Type, List, Dict, Tuple
from pydantic import BaseModel
from typing import TypedDict

class AgentState(TypedDict):
    start_url: str
    goal: str
    mode: str
    schema: Optional[Type[BaseModel]]

    to_visit: List[Tuple[str, int]]
    current_url: Optional[str]
    current_depth: int

    pages_raw: Dict[str, str]
    _current_links: List[str]

    chunks_extracted: Dict[str, List[Dict]]

    page_results: Dict[str, Dict]
    final_result: Optional[Dict]

    pages_processed: int
    done: bool
