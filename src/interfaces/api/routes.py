from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.application.orchestrator import ParseOrchestrator
from src.application.services.fetch_service import FetchService
from src.extractors.schemas.contact import ContactInfo
from src.extractors.schemas.organization import OrganizationInfo
from src.extractors.schemas.legal import LegalInfo


parse_router = APIRouter()
orchestrator = ParseOrchestrator()
fetch_service = FetchService()

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
def parse(request: ParseRequest):
    schema = SCHEMA_MAP.get(request.schema) if request.schema else None

    result = orchestrator.run(
        url=request.url,
        goal=request.goal,
        schema=schema,
        mode=request.mode,
        max_depth=request.max_depth,
        max_pages=request.max_pages
    )

    return result


@parse_router.get("/result")
def get_result(schema_key: str, url: str):
    result = fetch_service.get_results(schema_key, url)
    if  result is None:
        raise HTTPException(status_code=404)
    return {"result": result}