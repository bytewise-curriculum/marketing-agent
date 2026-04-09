from sqlalchemy.orm import Session
from app.agent.core import MarketingAgent
from app.providers import registry
from app.models.campaign import Campaign
from app.models.contact import Contact


async def create_and_send_email_blast(
    db: Session,
    name: str,
    topic: str,
    list_id: int | None = None,
    subject: str | None = None,
    html_body: str | None = None,
    goal: str = "engagement",
    tone: str = "professional",
    audience: str = "subscribers",
    send_now: bool = False,
    llm_provider: str | None = None,
    email_provider: str | None = None,
) -> Campaign:
    # Generate content if not provided
    if not html_body or not subject:
        agent = MarketingAgent(db, llm_provider)
        content = await agent.generate_email_content(
            topic=topic, goal=goal, tone=tone, audience=audience
        )
        if not subject:
            subject = content.metadata_.get("subject", f"Update: {topic}")
        if not html_body:
            html_body = content.body

    # Get recipients
    query = db.query(Contact).filter(Contact.subscribed == True)
    if list_id:
        query = query.filter(Contact.list_id == list_id)
    contacts = query.all()

    campaign = Campaign(
        type="email",
        name=name,
        subject=subject,
        body=html_body,
        status="draft",
        recipient_count=len(contacts),
        list_id=list_id,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    if send_now and contacts:
        email_svc = registry.get_email(email_provider)
        recipients = [{"email": c.email, "name": c.name} for c in contacts if c.email]

        results = await email_svc.send_batch(
            recipients=recipients,
            subject=subject,
            html_body=html_body,
        )

        success_count = sum(1 for r in results if r.success)
        campaign.status = "sent"
        campaign.recipient_count = success_count
        campaign.metadata_ = {
            "total_attempted": len(recipients),
            "successful": success_count,
            "failed": len(recipients) - success_count,
        }
        from datetime import datetime
        campaign.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(campaign)

    return campaign
