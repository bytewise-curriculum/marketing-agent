from sqlalchemy.orm import Session
from app.providers import registry
from app.models.campaign import Campaign
from app.models.contact import Contact


async def create_and_send_sms_blast(
    db: Session,
    name: str,
    message: str,
    list_id: int | None = None,
    send_now: bool = False,
    sms_provider: str | None = None,
) -> Campaign:
    # Get recipients
    query = db.query(Contact).filter(Contact.subscribed == True)
    if list_id:
        query = query.filter(Contact.list_id == list_id)
    contacts = query.all()

    campaign = Campaign(
        type="sms",
        name=name,
        body=message,
        status="draft",
        recipient_count=len(contacts),
        list_id=list_id,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    if send_now and contacts:
        sms_svc = registry.get_sms(sms_provider)
        phone_numbers = [c.phone for c in contacts if c.phone]

        results = await sms_svc.send_batch(
            recipients=phone_numbers,
            body=message,
        )

        success_count = sum(1 for r in results if r.success)
        campaign.status = "sent"
        campaign.recipient_count = success_count
        campaign.metadata_ = {
            "total_attempted": len(phone_numbers),
            "successful": success_count,
            "failed": len(phone_numbers) - success_count,
        }
        from datetime import datetime
        campaign.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(campaign)

    return campaign
