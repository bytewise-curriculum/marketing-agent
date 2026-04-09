from app.providers.registry import ProviderRegistry
from app.providers.llm.claude import ClaudeProvider
from app.providers.llm.openai_provider import OpenAIProvider
from app.providers.image.dalle import DalleProvider
from app.providers.image.nano_banana import NanoBananaProvider
from app.providers.video.runway import RunwayProvider
from app.providers.email.resend_provider import ResendProvider
from app.providers.sms.twilio_provider import TwilioProvider
from app.config import settings

registry = ProviderRegistry()

# Register all providers
registry.register_llm("claude", ClaudeProvider)
registry.register_llm("openai", OpenAIProvider)
registry.register_image("dalle", DalleProvider)
registry.register_image("nano_banana", NanoBananaProvider)
registry.register_video("runway", RunwayProvider)
registry.register_email("resend", ResendProvider)
registry.register_sms("twilio", TwilioProvider)

# Set active providers from config
registry.set_active("llm", settings.llm_provider)
registry.set_active("image", settings.image_provider)
registry.set_active("video", settings.video_provider)
registry.set_active("email", settings.email_provider)
registry.set_active("sms", settings.sms_provider)
