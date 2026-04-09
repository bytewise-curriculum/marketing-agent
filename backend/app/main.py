from fastapi import FastAPI
from app.config import settings
from app.models.database import create_tables
from app.routers import content, campaigns, contacts, training, providers

app = FastAPI(
    title=settings.app_name,
    description="AI-powered marketing agent for content creation and distribution",
    version="1.0.0",
)

app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])
app.include_router(providers.router, prefix="/api/providers", tags=["Providers"])


@app.on_event("startup")
async def startup():
    create_tables()


@app.get("/")
async def root():
    return {"name": settings.app_name, "status": "running"}
