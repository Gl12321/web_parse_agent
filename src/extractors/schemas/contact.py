from typing import List, Optional
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    phones: List[str] = Field(default_factory=list, description="Phone numbers found")
    emails: List[str] = Field(default_factory=list, description="Email addresses found")
    addresses: List[str] = Field(default_factory=list, description="Physical addresses or office locations")
    social_links: List[str] = Field(default_factory=list, description="Social media links (linkedin, twitter, facebook, etc)")
    website: Optional[str] = Field(None, description="Main website URL")
    contact_form: Optional[str] = Field(None, description="URL to contact form if available")
    working_hours: Optional[str] = Field(None, description="Business hours or working schedule")

    class Config:
        json_schema_extra = {
            "example": {
                "phones": ["+7 495 123-45-67", "+7 800 123-45-67"],
                "emails": ["info@company.com", "support@company.com"],
                "addresses": ["Moscow, Tverskaya st. 1", "St. Petersburg, Nevsky pr. 10"],
                "social_links": ["https://linkedin.com/company/example"],
                "website": "https://example.com",
                "contact_form": "https://example.com/contact",
                "working_hours": "Mon-Fri 9:00-18:00"
            }
        }
