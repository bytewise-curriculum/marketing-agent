from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Provider selection
    llm_provider: str = "claude"
    image_provider: str = "dalle"
    video_provider: str = "runway"
    email_provider: str = "resend"
    sms_provider: str = "twilio"

    # API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    resend_api_key: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None

    # Image provider keys
    nano_banana_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None

    # Video provider keys
    runway_api_key: Optional[str] = None
    pika_api_key: Optional[str] = None

    # Database
    database_url: str = "sqlite:///./marketing_agent.db"

    # App
    app_name: str = "Marketing AI Agent"
    default_from_email: str = "hello@yourdomain.com"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
