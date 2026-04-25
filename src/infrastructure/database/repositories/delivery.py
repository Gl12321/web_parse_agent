from typing import Optional, Dict, Any, Type

from src.infrastructure.database.models import ContactInfo, OrganizationInfo, LegalInfo
from src.infrastructure.database.postgres_client import PostgresClient


class DeliveryRepository:
    def __init__(self):
        self.session = PostgresClient().get_session()

    def get_by_schema_and_url(self, schema_key: str, source_url: str) -> Optional[Dict[str, Any]]:
        if schema_key == "contact":
            return self._get_contact_info(source_url)
        elif schema_key == "organization":
            return self._get_organization_info(source_url)
        elif schema_key == "legal":
            return self._get_legal_info(source_url)
        return None

    def _get_contact_info(self, source_url: str) -> Optional[Dict[str, Any]]:
        record = self.session.query(ContactInfo).filter_by(source_url=source_url).first()
        return {
            "phones": record.phones,
            "emails": record.emails,
            "addresses": record.addresses,
            "social_links": record.social_links,
            "website": record.website,
            "contact_form": record.contact_form,
            "working_hours": record.working_hours
        }

    def _get_organization_info(self, source_url: str) -> Optional[Dict[str, Any]]:
        record = self.session.query(OrganizationInfo).filter_by(source_url=source_url).first()
        if not record:
            return None
        return {
            "name": record.name,
            "description": record.description,
            "industry": record.industry,
            "founded": record.founded,
            "headquarters": record.headquarters,
            "employees": record.employees,
            "leadership": record.leadership,
            "values": record.values,
            "history": record.history
        }

    def _get_legal_info(self, source_url: str) -> Optional[Dict[str, Any]]:
        record = self.session.query(LegalInfo).filter_by(source_url=source_url).first()
        if not record:
            return None
        return {
            "inn": record.inn,
            "ogrn": record.ogrn,
            "kpp": record.kpp,
            "legal_form": record.legal_form,
            "registration_date": record.registration_date,
            "registration_authority": record.registration_authority,
            "licenses": record.licenses,
            "legal_address": record.legal_address,
            "bank_account": record.bank_account,
            "bik": record.bik,
            "bank_name": record.bank_name
        }
