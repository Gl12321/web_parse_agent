from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()


class ContactInfo(Base):
    __tablename__ = "contact_info"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    source_url = Column(String, nullable=False, index=True)
    phones = Column(ARRAY(String), default=list)
    emails = Column(ARRAY(String), default=list)
    addresses = Column(ARRAY(String), default=list)
    social_links = Column(ARRAY(String), default=list)
    website = Column(String, nullable=True)
    contact_form = Column(String, nullable=True)
    working_hours = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrganizationInfo(Base):
    __tablename__ = "organization_info"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    source_url = Column(String, nullable=False, index=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    founded = Column(String, nullable=True)
    headquarters = Column(String, nullable=True)
    employees = Column(String, nullable=True)
    leadership = Column(ARRAY(String), default=list)
    values = Column(ARRAY(String), default=list)
    history = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LegalInfo(Base):
    __tablename__ = "legal_info"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    source_url = Column(String, nullable=False, index=True)
    inn = Column(String, nullable=True)
    ogrn = Column(String, nullable=True)
    kpp = Column(String, nullable=True)
    legal_form = Column(String, nullable=True)
    registration_date = Column(String, nullable=True)
    registration_authority = Column(String, nullable=True)
    licenses = Column(ARRAY(String), default=list)
    legal_address = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)
    bik = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
