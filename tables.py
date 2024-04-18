from sqlalchemy import Column, String, Boolean, Float, Enum, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

from json_parser import BoolWithNA

Base = declarative_base()


class RetrievedInformation(Base):
    __tablename__ = "retrieved_information"
    url = Column(String, primary_key=True)
    long_answer = Column(String, primary_key=True)
    mortgage_register = Column(Enum(BoolWithNA))
    lands_regulated = Column(Enum(BoolWithNA))
    two_sided = Column(Enum(BoolWithNA))
    rent_administration_fee = Column(Float)


class Apartment(Base):
    __tablename__ = "apartments"

    url = Column(String(100), primary_key=True)
    table_dump = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
