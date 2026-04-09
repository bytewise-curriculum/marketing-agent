from sqlalchemy.orm import Session
from app.agent.core import MarketingAgent
from app.models.content import Content


async def create_newsletter(
    db: Session,
    topic: str,
    sections: int = 3,
    audience: str = "general",
    tone: str = "professional",
    llm_provider: str | None = None,
) -> Content:
    agent = MarketingAgent(db, llm_provider)
    return await agent.generate_newsletter(
        topic=topic,
        sections=sections,
        audience=audience,
        tone=tone,
    )
