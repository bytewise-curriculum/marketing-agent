import httpx
from app.providers.base import BaseImageProvider, ImageResponse
from app.config import settings


class NanoBananaProvider(BaseImageProvider):
    name = "nano_banana"

    def __init__(self):
        self.api_key = settings.nano_banana_api_key
        self.base_url = "https://api.nanobanana.com/v1"

    async def generate(
        self,
        prompt: str,
        style: str | None = None,
        width: int = 1024,
        height: int = 1024,
    ) -> ImageResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generate",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "prompt": prompt,
                    "style": style,
                    "width": width,
                    "height": height,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

        return ImageResponse(
            url=data.get("url", ""),
            provider="nano_banana",
            metadata=data,
        )
