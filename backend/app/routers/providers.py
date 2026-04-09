from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.providers import registry

router = APIRouter()


class SetActiveRequest(BaseModel):
    category: str  # llm, image, video, email, sms
    provider: str


@router.get("")
async def list_providers():
    return registry.list_providers()


@router.put("/active")
async def set_active_provider(req: SetActiveRequest):
    try:
        registry.set_active(req.category, req.provider)
        return {"category": req.category, "active": req.provider}
    except ValueError as e:
        raise HTTPException(400, str(e))
