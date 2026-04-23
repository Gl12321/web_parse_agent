from typing import List, Optional
from pydantic import BaseModel, Field


class ServiceInfo(BaseModel):
    name: Optional[str] = Field(None, description="Service or product name")
    description: Optional[str] = Field(None, description="Brief description")
    category: Optional[str] = Field(None, description="Service category or type")
    features: List[str] = Field(default_factory=list, description="Key features or capabilities")
    pricing: Optional[str] = Field(None, description="Pricing information or range")
    target_audience: Optional[str] = Field(None, description="Target customers or audience")


class ServicesList(BaseModel):
    services: List[ServiceInfo] = Field(default_factory=list, description="List of services or products offered")
    categories: List[str] = Field(default_factory=list, description="Available service categories")

    class Config:
        json_schema_extra = {
            "example": {
                "services": [
                    {
                        "name": "Web Development",
                        "description": "Custom web application development",
                        "category": "Development",
                        "features": ["Responsive design", "SEO optimization"],
                        "pricing": "From $5000"
                    }
                ],
                "categories": ["Development", "Design", "Consulting"]
            }
        }
