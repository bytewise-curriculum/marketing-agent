from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.models.database import get_db
from app.models.training import TrainingFeedback, PromptTemplate
from app.models.content import Content
from app.agent.training import get_content_analytics, seed_default_prompts

router = APIRouter()


class FeedbackCreate(BaseModel):
    content_id: int
    rating: int  # 1-5
    feedback_text: Optional[str] = None


class PromptTemplateUpdate(BaseModel):
    template_text: str
    name: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(req: FeedbackCreate, db: Session = Depends(get_db)):
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(400, "Rating must be between 1 and 5")

    content = db.query(Content).filter(Content.id == req.content_id).first()
    if not content:
        raise HTTPException(404, "Content not found")

    feedback = TrainingFeedback(
        content_id=req.content_id,
        rating=req.rating,
        feedback_text=req.feedback_text,
        original_prompt=content.prompt_used,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {"id": feedback.id, "content_id": feedback.content_id, "rating": feedback.rating}


@router.get("/feedback")
async def list_feedback(
    content_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(TrainingFeedback)
    if content_type:
        query = query.join(Content, TrainingFeedback.content_id == Content.id).filter(
            Content.type == content_type
        )

    items = query.order_by(TrainingFeedback.created_at.desc()).limit(limit).all()
    return [
        {
            "id": fb.id,
            "content_id": fb.content_id,
            "rating": fb.rating,
            "feedback_text": fb.feedback_text,
            "created_at": str(fb.created_at),
        }
        for fb in items
    ]


@router.get("/analytics")
async def analytics(db: Session = Depends(get_db)):
    return get_content_analytics(db)


@router.get("/prompts")
async def list_prompts(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(PromptTemplate)
    if type:
        query = query.filter(PromptTemplate.type == type)

    templates = query.order_by(PromptTemplate.type, PromptTemplate.version.desc()).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "type": t.type,
            "template_text": t.template_text,
            "version": t.version,
            "is_active": t.is_active,
            "created_at": str(t.created_at),
        }
        for t in templates
    ]


@router.put("/prompts/{prompt_id}")
async def update_prompt(prompt_id: int, update: PromptTemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not template:
        raise HTTPException(404, "Prompt template not found")

    # Deactivate old version
    template.is_active = False
    db.commit()

    # Create new version
    new_template = PromptTemplate(
        name=update.name or template.name,
        type=template.type,
        template_text=update.template_text,
        version=template.version + 1,
        is_active=True,
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return {
        "id": new_template.id,
        "name": new_template.name,
        "type": new_template.type,
        "version": new_template.version,
        "is_active": new_template.is_active,
    }


@router.post("/prompts/seed")
async def seed_prompts(db: Session = Depends(get_db)):
    seed_default_prompts(db)
    return {"status": "seeded"}
