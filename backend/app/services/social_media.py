from sqlalchemy.orm import Session
from app.agent.core import MarketingAgent
from app.providers import registry
from app.models.content import Content


PLATFORM_LIMITS = {
    "twitter": 280,
    "instagram": 2200,
    "linkedin": 3000,
    "facebook": 63206,
    "tiktok": 2200,
    "threads": 500,
}


async def create_social_post(
    db: Session,
    platform: str,
    topic: str,
    tone: str = "professional",
    generate_image: bool = False,
    llm_provider: str | None = None,
    image_provider: str | None = None,
) -> Content:
    agent = MarketingAgent(db, llm_provider)
    max_length = PLATFORM_LIMITS.get(platform, 280)

    content = await agent.generate_social_post(
        platform=platform,
        topic=topic,
        tone=tone,
        max_length=max_length,
    )

    if generate_image:
        image_prompt = await agent.generate_image_prompt(
            purpose=f"Social media image for {platform}",
            brand=topic,
            style="modern social media",
            platform=platform,
        )
        try:
            image_gen = registry.get_image(image_provider)
            image_result = await image_gen.generate(prompt=image_prompt)
            content.metadata_ = content.metadata_ or {}
            content.metadata_["image_url"] = image_result.url
            content.metadata_["image_prompt"] = image_prompt
            db.commit()
            db.refresh(content)
        except Exception as e:
            content.metadata_ = content.metadata_ or {}
            content.metadata_["image_error"] = str(e)
            content.metadata_["image_prompt"] = image_prompt
            db.commit()

    return content
