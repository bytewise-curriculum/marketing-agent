from twilio.rest import Client
from app.providers.base import BaseSMSProvider, SMSResult
from app.config import settings


class TwilioProvider(BaseSMSProvider):
    name = "twilio"

    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_number = settings.twilio_phone_number

    async def send(self, to: str, body: str) -> SMSResult:
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=to,
            )
            return SMSResult(success=True, message_id=message.sid)
        except Exception as e:
            return SMSResult(success=False, error=str(e))

    async def send_batch(self, recipients: list[str], body: str) -> list[SMSResult]:
        results = []
        for phone in recipients:
            result = await self.send(phone, body)
            results.append(result)
        return results
