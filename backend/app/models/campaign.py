from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # email, sms
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)  # email subject
    body = Column(Text, nullable=False)
    status = Column(String(20), default="draft")  # draft, scheduled, sent, failed
    recipient_count = Column(Integer, default=0)
    list_id = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
