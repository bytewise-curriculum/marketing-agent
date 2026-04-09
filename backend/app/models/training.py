from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.models.database import Base


class TrainingFeedback(Base):
    __tablename__ = "training_feedback"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    feedback_text = Column(Text, nullable=True)
    original_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # social_post, newsletter, video_script, etc.
    template_text = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
