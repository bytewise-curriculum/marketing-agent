from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # social_post, newsletter, video_script, short_video_script, image
    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    platform = Column(String(50), nullable=True)  # twitter, instagram, linkedin, tiktok, youtube, etc.
    status = Column(String(20), default="draft")  # draft, published
    metadata_ = Column("metadata", JSON, nullable=True)  # extra data (image_url, video_url, etc.)
    prompt_used = Column(Text, nullable=True)
    llm_provider = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
