from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Boolean, String
from dataclasses_json import dataclass_json
from haneen_app.entities.sitter import Sitter

Base = declarative_base()

@dataclass_json
class Parent(Base):
    __table_args__ = {"schema": "public"}
    __tablename__ = "t_parent"

    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String)
    last_name  = Column(String)
    username = Column(String)
    password = Column(String)
    email_address = Column(String)
    phone_number = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zip_code = Column(String)
    is_active = Column(Boolean, default=True)
    sitter_id = Column(BigInteger, foreign_key=Sitter.user_id, default=None)