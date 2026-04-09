from sqlalchemy.orm import Session
from app.agent.core import MarketingAgent
from app.providers import registry
from app.models.content import Content


async def create_video_script(
    db: Session,
    topic: str,
    duration: int = 60,
    style: str = "educational",
    audience: str = "general",
    generate_video: bool = False,
    llm_provider: str | None = None,
    video_provider: str | None = None,
) -> Content:
    agent = MarketingAgent(db, llm_provider)
    content = await agent.generate_video_script(
        topic=topic,
        duration=duration,
        style=style,
        audience=audience,
    )

    if generate_video:
        try:
            video_gen = registry.get_video(video_provider)
            video_result = await video_gen.generate(
                prompt=f"{topic} - {style} style",
                duration=duration,
            )
            content.metadata_ = content.metadata_ or {}
            content.metadata_["video_url"] = video_result.url
            content.metadata_["video_status"] = video_result.status
            db.commit()
            db.refresh(content)
        except Exception as e:
            content.metadata_ = content.metadata_ or {}
            content.metadata_["video_error"] = str(e)
            db.commit()

    return content


async def create_short_video_script(
    db: Session,
    topic: str,
    platform: str = "tiktok",
    duration: int = 30,
    style: str = "trendy",
    generate_video: bool = False,
    llm_provider: str | None = None,
    video_provider: str | None = None,
) -> Content:
    agent = MarketingAgent(db, llm_provider)
    content = await agent.generate_short_video_script(
        topic=topic,
        platform=platform,
        duration=duration,
        style=style,
    )

    if generate_video:
        try:
            video_gen = registry.get_video(video_provider)
            video_result = await video_gen.generate(
                prompt=f"Short form video: {topic} - {style}",
                duration=min(duration, 10),
            )
            content.metadata_ = content.metadata_ or {}
            content.metadata_["video_url"] = video_result.url
            content.metadata_["video_status"] = video_result.status
            db.commit()
            db.refresh(content)
        except Exception as e:
            content.metadata_ = content.metadata_ or {}
            content.metadata_["video_error"] = str(e)
            db.commit()

    return content
