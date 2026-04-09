from app.providers.base import (
    BaseLLMProvider,
    BaseImageProvider,
    BaseVideoProvider,
    BaseEmailProvider,
    BaseSMSProvider,
)


class ProviderRegistry:
    def __init__(self):
        self._llm_providers: dict[str, type[BaseLLMProvider]] = {}
        self._image_providers: dict[str, type[BaseImageProvider]] = {}
        self._video_providers: dict[str, type[BaseVideoProvider]] = {}
        self._email_providers: dict[str, type[BaseEmailProvider]] = {}
        self._sms_providers: dict[str, type[BaseSMSProvider]] = {}

        self._active: dict[str, str] = {}
        self._instances: dict[str, object] = {}

    def register_llm(self, name: str, provider_class: type[BaseLLMProvider]):
        self._llm_providers[name] = provider_class

    def register_image(self, name: str, provider_class: type[BaseImageProvider]):
        self._image_providers[name] = provider_class

    def register_video(self, name: str, provider_class: type[BaseVideoProvider]):
        self._video_providers[name] = provider_class

    def register_email(self, name: str, provider_class: type[BaseEmailProvider]):
        self._email_providers[name] = provider_class

    def register_sms(self, name: str, provider_class: type[BaseSMSProvider]):
        self._sms_providers[name] = provider_class

    def _get_instance(self, category: str, providers: dict, name: str):
        key = f"{category}:{name}"
        if key not in self._instances:
            if name not in providers:
                raise ValueError(
                    f"Provider '{name}' not found for {category}. "
                    f"Available: {list(providers.keys())}"
                )
            self._instances[key] = providers[name]()
        return self._instances[key]

    def get_llm(self, name: str | None = None) -> BaseLLMProvider:
        name = name or self._active.get("llm", "claude")
        return self._get_instance("llm", self._llm_providers, name)

    def get_image(self, name: str | None = None) -> BaseImageProvider:
        name = name or self._active.get("image", "dalle")
        return self._get_instance("image", self._image_providers, name)

    def get_video(self, name: str | None = None) -> BaseVideoProvider:
        name = name or self._active.get("video", "runway")
        return self._get_instance("video", self._video_providers, name)

    def get_email(self, name: str | None = None) -> BaseEmailProvider:
        name = name or self._active.get("email", "resend")
        return self._get_instance("email", self._email_providers, name)

    def get_sms(self, name: str | None = None) -> BaseSMSProvider:
        name = name or self._active.get("sms", "twilio")
        return self._get_instance("sms", self._sms_providers, name)

    def set_active(self, category: str, name: str):
        valid_categories = {
            "llm": self._llm_providers,
            "image": self._image_providers,
            "video": self._video_providers,
            "email": self._email_providers,
            "sms": self._sms_providers,
        }
        if category not in valid_categories:
            raise ValueError(f"Invalid category: {category}")
        if name not in valid_categories[category]:
            raise ValueError(
                f"Provider '{name}' not registered for {category}. "
                f"Available: {list(valid_categories[category].keys())}"
            )
        self._active[category] = name

    def list_providers(self) -> dict:
        return {
            "llm": {
                "available": list(self._llm_providers.keys()),
                "active": self._active.get("llm", "claude"),
            },
            "image": {
                "available": list(self._image_providers.keys()),
                "active": self._active.get("image", "dalle"),
            },
            "video": {
                "available": list(self._video_providers.keys()),
                "active": self._active.get("video", "runway"),
            },
            "email": {
                "available": list(self._email_providers.keys()),
                "active": self._active.get("email", "resend"),
            },
            "sms": {
                "available": list(self._sms_providers.keys()),
                "active": self._active.get("sms", "twilio"),
            },
        }
