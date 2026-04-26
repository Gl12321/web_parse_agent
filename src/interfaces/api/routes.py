import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.application.orchestrator import ParseOrchestrator
from src.application.services.fetch_service import FetchService
from src.extractors.schemas.contact import ContactInfo
from src.extractors.schemas.organization import OrganizationInfo
from src.extractors.schemas.legal import LegalInfo


parse_router = APIRouter()
fetch_service = FetchService()

executor = ProcessPoolExecutor(max_workers=3)


def _run_parsing(url: str, goal: str, schema, mode: str, max_depth: int, max_pages: int):
    orchestrator = ParseOrchestrator()
    return orchestrator.run(
        url=url,
        goal=goal,
        schema=schema,
        mode=mode,
        max_depth=max_depth,
        max_pages=max_pages
    )

SCHEMA_MAP = {
    "contact": ContactInfo,
    "organization": OrganizationInfo,
    "legal": LegalInfo,
}


class ParseRequest(BaseModel):
    url: str
    goal: str
    schema: str = None
    mode: str = "flexible"
    max_depth: int = 3
    max_pages: int = 5

class ResultRequest(BaseModel):
    schema_key: str
    url: str


@parse_router.post("/parse")
async def parse(request: ParseRequest):
    schema = SCHEMA_MAP.get(request.schema) if request.schema else None

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        _run_parsing,
        request.url,
        request.goal,
        schema,
        request.mode,
        request.max_depth,
        request.max_pages
    )

    return result


@parse_router.get("/result")
async def get_result(schema_key: str, url: str):
    result = fetch_service.get_results(schema_key, url)
    if result is None:
        raise HTTPException(status_code=404)
    return {"result": result}