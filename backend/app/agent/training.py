from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.training import TrainingFeedback, PromptTemplate
from app.models.content import Content
from app.agent.prompts import DEFAULT_PROMPTS


def get_feedback_context(db: Session, content_type: str, limit: int = 5) -> str:
    feedback_entries = (
        db.query(TrainingFeedback)
        .join(Content, TrainingFeedback.content_id == Content.id)
        .filter(Content.type == content_type)
        .filter(TrainingFeedback.rating >= 4)
        .order_by(TrainingFeedback.created_at.desc())
        .limit(limit)
        .all()
    )

    if not feedback_entries:
        return ""

    context_parts = ["Based on previous successful content, keep in mind:"]
    for fb in feedback_entries:
        if fb.feedback_text:
            context_parts.append(f"- {fb.feedback_text}")

    return "\n".join(context_parts)


def get_content_analytics(db: Session) -> dict:
    stats = {}
    content_types = db.query(Content.type).distinct().all()

    for (ctype,) in content_types:
        avg_rating = (
            db.query(func.avg(TrainingFeedback.rating))
            .join(Content, TrainingFeedback.content_id == Content.id)
            .filter(Content.type == ctype)
            .scalar()
        )

        total_content = db.query(Content).filter(Content.type == ctype).count()
        total_feedback = (
            db.query(TrainingFeedback)
            .join(Content, TrainingFeedback.content_id == Content.id)
            .filter(Content.type == ctype)
            .count()
        )

        stats[ctype] = {
            "total_content": total_content,
            "total_feedback": total_feedback,
            "average_rating": round(float(avg_rating), 2) if avg_rating else None,
        }

    return stats


def seed_default_prompts(db: Session):
    existing = db.query(PromptTemplate).count()
    if existing > 0:
        return

    for ptype, pdata in DEFAULT_PROMPTS.items():
        template = PromptTemplate(
            name=pdata["name"],
            type=ptype,
            template_text=pdata["template"],
            version=1,
            is_active=True,
        )
        db.add(template)

    db.commit()
