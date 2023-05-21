from sqlalchemy import Column, String, Text, create_engine, DateTime
from sqlalchemy.orm import declarative_base, Session

engine = create_engine(f'sqlite:///emails.db?charset=utf8')
Base = declarative_base()

class Emails(Base):
    __tablename__ = "emails"
    id = Column(String, primary_key=True)
    thread_id = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    subject = Column(String)
    body = Column(Text)
    received_date = Column(DateTime, nullable=False)



if __name__ == "__main__":
    Base.metadata.create_all(engine)
