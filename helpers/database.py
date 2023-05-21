from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()
engine = create_engine(f'sqlite:///emails.db?charset=utf8')

class Emails(Base):
    __tablename__ = "emails"
    id = Column(String, primary_key=True)
    sender = Column(String, nullable=False)
    subject = Column(String)
    body = Column(Text)
    received_date = Column(DateTime, nullable=False)

def create_db():
    Base.metadata.create_all(engine)
