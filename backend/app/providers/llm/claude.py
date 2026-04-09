import anthropic
from app.providers.base import BaseLLMProvider, LLMResponse
from app.config import settings


class ClaudeProvider(BaseLLMProvider):
    name = "claude"

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt if system_prompt else "",
            messages=[{"role": "user", "content": prompt}],
        )
        return LLMResponse(
            text=message.content[0].text,
            model=self.model,
            usage={
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            },
        )
