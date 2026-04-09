from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.models.database import get_db
from app.models.content import Content
from app.services.social_media import create_social_post
from app.services.newsletter import create_newsletter
from app.services.video import create_video_script, create_short_video_script
from app.providers import registry

router = APIRouter()


class GenerateRequest(BaseModel):
    type: str  # social_post, newsletter, video_script, short_video_script
    topic: str
    platform: Optional[str] = None
    tone: Optional[str] = "professional"
    sections: Optional[int] = 3
    audience: Optional[str] = "general"
    duration: Optional[int] = 60
    style: Optional[str] = None
    generate_image: Optional[bool] = False
    generate_video: Optional[bool] = False
    llm_provider: Optional[str] = None
    image_provider: Optional[str] = None
    video_provider: Optional[str] = None


class GenerateImageRequest(BaseModel):
    prompt: str
    style: Optional[str] = None
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    provider: Optional[str] = None


class ContentResponse(BaseModel):
    id: int
    type: str
    title: Optional[str]
    body: str
    platform: Optional[str]
    status: str
    metadata: Optional[dict]
    llm_provider: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = None


@router.post("/generate")
async def generate_content(req: GenerateRequest, db: Session = Depends(get_db)):
    if req.type == "social_post":
        if not req.platform:
            raise HTTPException(400, "platform is required for social posts")
        content = await create_social_post(
            db=db,
            platform=req.platform,
            topic=req.topic,
            tone=req.tone,
            generate_image=req.generate_image,
            llm_provider=req.llm_provider,
            image_provider=req.image_provider,
        )
    elif req.type == "newsletter":
        content = await create_newsletter(
            db=db,
            topic=req.topic,
            sections=req.sections,
            audience=req.audience,
            tone=req.tone,
            llm_provider=req.llm_provider,
        )
    elif req.type == "video_script":
        content = await create_video_script(
            db=db,
            topic=req.topic,
            duration=req.duration,
            style=req.style or "educational",
            audience=req.audience,
            generate_video=req.generate_video,
            llm_provider=req.llm_provider,
            video_provider=req.video_provider,
        )
    elif req.type == "short_video_script":
        content = await create_short_video_script(
            db=db,
            topic=req.topic,
            platform=req.platform or "tiktok",
            duration=req.duration or 30,
            style=req.style or "trendy",
            generate_video=req.generate_video,
            llm_provider=req.llm_provider,
            video_provider=req.video_provider,
        )
    else:
        raise HTTPException(400, f"Unknown content type: {req.type}")

    return {
        "id": content.id,
        "type": content.type,
        "title": content.title,
        "body": content.body,
        "platform": content.platform,
        "status": content.status,
        "metadata": content.metadata_,
        "llm_provider": content.llm_provider,
        "created_at": str(content.created_at),
    }


@router.post("/generate-image")
async def generate_image(req: GenerateImageRequest):
    try:
        image_gen = registry.get_image(req.provider)
        result = await image_gen.generate(
            prompt=req.prompt,
            style=req.style,
            width=req.width,
            height=req.height,
        )
        return {"url": result.url, "provider": result.provider, "metadata": result.metadata}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("")
async def list_content(
    type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Content)
    if type:
        query = query.filter(Content.type == type)
    if status:
        query = query.filter(Content.status == status)

    total = query.count()
    items = query.order_by(Content.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": c.id,
                "type": c.type,
                "title": c.title,
                "body": c.body[:200] + "..." if len(c.body) > 200 else c.body,
                "platform": c.platform,
                "status": c.status,
                "llm_provider": c.llm_provider,
                "created_at": str(c.created_at),
            }
            for c in items
        ],
    }


@router.get("/{content_id}")
async def get_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(404, "Content not found")
    return {
        "id": content.id,
        "type": content.type,
        "title": content.title,
        "body": content.body,
        "platform": content.platform,
        "status": content.status,
        "metadata": content.metadata_,
        "prompt_used": content.prompt_used,
        "llm_provider": content.llm_provider,
        "created_at": str(content.created_at),
        "updated_at": str(content.updated_at),
    }


@router.put("/{content_id}")
async def update_content(content_id: int, update: ContentUpdate, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(404, "Content not found")

    if update.title is not None:
        content.title = update.title
    if update.body is not None:
        content.body = update.body
    if update.status is not None:
        content.status = update.status

    db.commit()
    db.refresh(content)
    return {"id": content.id, "status": "updated"}
