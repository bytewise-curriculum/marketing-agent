from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    model: str
    usage: dict | None = None


@dataclass
class ImageResponse:
    url: str
    provider: str
    metadata: dict | None = None


@dataclass
class VideoResponse:
    url: str
    provider: str
    status: str = "completed"  # completed, processing
    metadata: dict | None = None


@dataclass
class EmailResult:
    success: bool
    message_id: str | None = None
    error: str | None = None


@dataclass
class SMSResult:
    success: bool
    message_id: str | None = None
    error: str | None = None


class BaseLLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        pass


class BaseImageProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        style: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> ImageResponse:
        pass


class BaseVideoProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        duration: int = 15,
        style: Optional[str] = None,
    ) -> VideoResponse:
        pass


class BaseEmailProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def send(
        self,
        to: str | list[str],
        subject: str,
        html_body: str,
        from_email: str | None = None,
    ) -> EmailResult:
        pass

    @abstractmethod
    async def send_batch(
        self,
        recipients: list[dict],
        subject: str,
        html_body: str,
        from_email: str | None = None,
    ) -> list[EmailResult]:
        pass


class BaseSMSProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def send(self, to: str, body: str) -> SMSResult:
        pass

    @abstractmethod
    async def send_batch(self, recipients: list[str], body: str) -> list[SMSResult]:
        pass
