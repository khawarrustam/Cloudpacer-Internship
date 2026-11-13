"""Resend implementation of the domain email sender port."""

import resend

from app.domain.notification import EmailMessage, EmailSender


class ResendEmailSender(EmailSender):
    """What: Send transactional reminder emails through Resend.

    When: ReminderService finds an unsent reminder whose time has arrived.
    How: Use one API key and a stable idempotency key for safe retries.
    """

    def __init__(self, api_key: str, sender: str) -> None:
        clean_key = api_key.strip()
        clean_sender = sender.strip()
        if not clean_key or clean_key.startswith("replace-with-"):
            raise RuntimeError("Add RESEND_API_KEY before starting the API.")
        if not clean_sender:
            raise RuntimeError("Add REMINDER_EMAIL_FROM before starting the API.")
        self.api_key = clean_key
        self.sender = clean_sender

    def send(self, message: EmailMessage) -> str:
        """Send one reminder and return Resend's email ID."""
        resend.api_key = self.api_key
        response = resend.Emails.send(
            {
                "from": self.sender,
                "to": [message.recipient],
                "subject": message.subject,
                "html": message.html,
                "text": message.text,
            },
            # Resend Python SDK options second argument mein leta hai. Stable
            # key same reminder ki safe retry ko duplicate email se bachati hai.
            {"idempotency_key": message.idempotency_key},
        )
        email_id = response.get("id")
        if not email_id:
            raise RuntimeError("Resend did not return an email ID.")
        return str(email_id)
