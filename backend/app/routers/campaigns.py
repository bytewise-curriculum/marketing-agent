from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.models.database import get_db
from app.models.campaign import Campaign
from app.services.email_blast import create_and_send_email_blast
from app.services.sms_blast import create_and_send_sms_blast

router = APIRouter()


class EmailBlastRequest(BaseModel):
    name: str
    topic: str
    list_id: Optional[int] = None
    subject: Optional[str] = None
    html_body: Optional[str] = None
    goal: Optional[str] = "engagement"
    tone: Optional[str] = "professional"
    audience: Optional[str] = "subscribers"
    send_now: Optional[bool] = False
    llm_provider: Optional[str] = None
    email_provider: Optional[str] = None


class SMSBlastRequest(BaseModel):
    name: str
    message: str
    list_id: Optional[int] = None
    send_now: Optional[bool] = False
    sms_provider: Optional[str] = None


@router.post("/email")
async def create_email_blast(req: EmailBlastRequest, db: Session = Depends(get_db)):
    campaign = await create_and_send_email_blast(
        db=db,
        name=req.name,
        topic=req.topic,
        list_id=req.list_id,
        subject=req.subject,
        html_body=req.html_body,
        goal=req.goal,
        tone=req.tone,
        audience=req.audience,
        send_now=req.send_now,
        llm_provider=req.llm_provider,
        email_provider=req.email_provider,
    )
    return {
        "id": campaign.id,
        "name": campaign.name,
        "type": campaign.type,
        "subject": campaign.subject,
        "status": campaign.status,
        "recipient_count": campaign.recipient_count,
        "metadata": campaign.metadata_,
        "created_at": str(campaign.created_at),
    }


@router.post("/sms")
async def create_sms_blast(req: SMSBlastRequest, db: Session = Depends(get_db)):
    campaign = await create_and_send_sms_blast(
        db=db,
        name=req.name,
        message=req.message,
        list_id=req.list_id,
        send_now=req.send_now,
        sms_provider=req.sms_provider,
    )
    return {
        "id": campaign.id,
        "name": campaign.name,
        "type": campaign.type,
        "status": campaign.status,
        "recipient_count": campaign.recipient_count,
        "metadata": campaign.metadata_,
        "created_at": str(campaign.created_at),
    }


@router.get("")
async def list_campaigns(
    type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Campaign)
    if type:
        query = query.filter(Campaign.type == type)
    if status:
        query = query.filter(Campaign.status == status)

    total = query.count()
    items = query.order_by(Campaign.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "subject": c.subject,
                "status": c.status,
                "recipient_count": c.recipient_count,
                "sent_at": str(c.sent_at) if c.sent_at else None,
                "created_at": str(c.created_at),
            }
            for c in items
        ],
    }


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return {
        "id": campaign.id,
        "name": campaign.name,
        "type": campaign.type,
        "subject": campaign.subject,
        "body": campaign.body,
        "status": campaign.status,
        "recipient_count": campaign.recipient_count,
        "metadata": campaign.metadata_,
        "sent_at": str(campaign.sent_at) if campaign.sent_at else None,
        "created_at": str(campaign.created_at),
    }
