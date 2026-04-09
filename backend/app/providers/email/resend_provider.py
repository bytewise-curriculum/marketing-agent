import resend
from app.providers.base import BaseEmailProvider, EmailResult
from app.config import settings


class ResendProvider(BaseEmailProvider):
    name = "resend"

    def __init__(self):
        resend.api_key = settings.resend_api_key
        self.from_email = settings.default_from_email

    async def send(
        self,
        to: str | list[str],
        subject: str,
        html_body: str,
        from_email: str | None = None,
    ) -> EmailResult:
        try:
            result = resend.Emails.send(
                {
                    "from": from_email or self.from_email,
                    "to": to if isinstance(to, list) else [to],
                    "subject": subject,
                    "html": html_body,
                }
            )
            return EmailResult(success=True, message_id=result.get("id"))
        except Exception as e:
            return EmailResult(success=False, error=str(e))

    async def send_batch(
        self,
        recipients: list[dict],
        subject: str,
        html_body: str,
        from_email: str | None = None,
    ) -> list[EmailResult]:
        results = []
        batch = [
            {
                "from": from_email or self.from_email,
                "to": [r["email"]],
                "subject": subject,
                "html": html_body,
            }
            for r in recipients
        ]
        try:
            response = resend.Batch.send(batch)
            for item in response.get("data", []):
                results.append(EmailResult(success=True, message_id=item.get("id")))
        except Exception as e:
            results.append(EmailResult(success=False, error=str(e)))
        return results
