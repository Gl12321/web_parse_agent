from typing import List, Optional
from pydantic import BaseModel, Field


class OrganizationInfo(BaseModel):
    name: Optional[str] = Field(None, description="Company or organization name")
    description: Optional[str] = Field(None, description="Brief description of the organization")
    industry: Optional[str] = Field(None, description="Industry or sector")
    founded: Optional[str] = Field(None, description="Year founded or establishment date")
    headquarters: Optional[str] = Field(None, description="Headquarters location")
    employees: Optional[str] = Field(None, description="Number of employees or range")
    leadership: List[str] = Field(default_factory=list, description="Key executives or leadership team")
    values: List[str] = Field(default_factory=list, description="Company values or mission")
    history: Optional[str] = Field(None, description="Brief history or background")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Example Corp",
                "description": "Leading provider of example solutions",
                "industry": "Technology",
                "founded": "2010",
                "headquarters": "Moscow, Russia",
                "employees": "100-500",
                "leadership": ["John Doe - CEO", "Jane Smith - CTO"],
                "values": ["Innovation", "Customer First", "Integrity"]
            }
        }
