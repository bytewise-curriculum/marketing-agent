from openai import OpenAI
from app.providers.base import BaseImageProvider, ImageResponse
from app.config import settings


class DalleProvider(BaseImageProvider):
    name = "dalle"

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    async def generate(
        self,
        prompt: str,
        style: str | None = None,
        width: int = 1024,
        height: int = 1024,
    ) -> ImageResponse:
        size = f"{width}x{height}"
        if size not in ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]:
            size = "1024x1024"

        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            style=style or "vivid",
            n=1,
        )
        return ImageResponse(
            url=response.data[0].url,
            provider="dalle",
            metadata={"revised_prompt": response.data[0].revised_prompt},
        )
