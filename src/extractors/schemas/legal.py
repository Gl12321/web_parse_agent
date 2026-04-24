from typing import List, Optional
from pydantic import BaseModel, Field


class LegalInfo(BaseModel):
    inn: Optional[str] = Field(None, description="Tax identification number (ИНН)")
    ogrn: Optional[str] = Field(None, description="Main state registration number (ОГРН)")
    kpp: Optional[str] = Field(None, description="Tax registration reason code (КПП)")
    legal_form: Optional[str] = Field(None, description="Legal form of organization")
    registration_date: Optional[str] = Field(None, description="Date of state registration")
    registration_authority: Optional[str] = Field(None, description="Authority that performed registration")
    licenses: List[str] = Field(default_factory=list, description="List of licenses and permits")
    legal_address: Optional[str] = Field(None, description="Legal registration address")
    bank_account: Optional[str] = Field(None, description="Bank account number")
    bik: Optional[str] = Field(None, description="Bank identification code (БИК)")
    bank_name: Optional[str] = Field(None, description="Name of the bank")

    class Config:
        json_schema_extra = {
            "example": {
                "inn": "7707083893",
                "ogrn": "1027700132195",
                "kpp": "773601001",
                "legal_form": "ООО",
                "registration_date": "2000-06-29",
                "registration_authority": "Московская регистрационная палата",
                "licenses": ["Лицензия на телематические услуги", "Лицензия на услуги связи"],
                "legal_address": "г. Москва, ул. Льва Толстого, д. 16",
                "bank_account": "40702810100000000000",
                "bik": "044525225",
                "bank_name": "ПАО Сбербанк"
            }
        }
