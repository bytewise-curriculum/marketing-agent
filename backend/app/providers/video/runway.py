import httpx
from app.providers.base import BaseVideoProvider, VideoResponse
from app.config import settings


class RunwayProvider(BaseVideoProvider):
    name = "runway"

    def __init__(self):
        self.api_key = settings.runway_api_key
        self.base_url = "https://api.dev.runwayml.com/v1"

    async def generate(
        self,
        prompt: str,
        duration: int = 15,
        style: str | None = None,
    ) -> VideoResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/image_to_video",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "X-Runway-Version": "2024-11-06",
                },
                json={
                    "model": "gen4_turbo",
                    "promptText": prompt,
                    "duration": min(duration, 10),
                    "ratio": "16:9",
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

        return VideoResponse(
            url=data.get("url", ""),
            provider="runway",
            status="processing" if data.get("status") == "RUNNING" else "completed",
            metadata=data,
        )
