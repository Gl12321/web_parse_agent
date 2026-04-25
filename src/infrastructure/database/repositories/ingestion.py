from src.infrastructure.database.models import ContactInfo, OrganizationInfo, LegalInfo, Base
from src.infrastructure.database.postgres_client import PostgresClient


class ExtractionRepository:
    def __init__(self):
        self.create_tables()
        self.session = PostgresClient().get_session()

    def create_tables(self):
        client = PostgresClient()
        Base.metadata.create_all(client.engine)

    def save_contact_info(self, source_url: str, data: dict):
        record = ContactInfo(
            source_url=source_url,
            phones=data.get("phones", []),
            emails=data.get("emails", []),
            addresses=data.get("addresses", []),
            social_links=data.get("social_links", []),
            website=data.get("website"),
            contact_form=data.get("contact_form"),
            working_hours=data.get("working_hours")
        )
        self.session.add(record)
        self.session.commit()
        return record

    def save_organization_info(self, source_url: str, data: dict):
        record = OrganizationInfo(
            source_url=source_url,
            name=data.get("name"),
            description=data.get("description"),
            industry=data.get("industry"),
            founded=data.get("founded"),
            headquarters=data.get("headquarters"),
            employees=data.get("employees"),
            leadership=data.get("leadership", []),
            values=data.get("values", []),
            history=data.get("history")
        )
        self.session.add(record)
        self.session.commit()
        return record

    def save_legal_info(self, source_url: str, data: dict):
        record = LegalInfo(
            source_url=source_url,
            inn=data.get("inn"),
            ogrn=data.get("ogrn"),
            kpp=data.get("kpp"),
            legal_form=data.get("legal_form"),
            registration_date=data.get("registration_date"),
            registration_authority=data.get("registration_authority"),
            licenses=data.get("licenses", []),
            legal_address=data.get("legal_address"),
            bank_account=data.get("bank_account"),
            bik=data.get("bik"),
            bank_name=data.get("bank_name")
        )
        self.session.add(record)
        self.session.commit()
        return record