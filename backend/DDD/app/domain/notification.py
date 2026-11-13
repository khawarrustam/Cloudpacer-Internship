"""Database and provider-independent email notification contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.auth import EmailAddress


@dataclass(frozen=True)
class EmailMessage:
    """A validated transactional email requested by an application use case."""

    recipient: str
    subject: str
    html: str
    text: str
    idempotency_key: str

    def __post_init__(self) -> None:
        clean_recipient = EmailAddress(self.recipient).value
        clean_subject = self.subject.strip()
        clean_key = self.idempotency_key.strip()
        if not clean_subject:
            raise ValueError("Email subject cannot be empty.")
        if not clean_key or len(clean_key) > 256:
            raise ValueError("Email idempotency key must be 1 to 256 characters.")
        object.__setattr__(self, "recipient", clean_recipient)
        object.__setattr__(self, "subject", clean_subject)
        object.__setattr__(self, "idempotency_key", clean_key)


class EmailSender(ABC):
    """Outgoing port implemented by an email provider such as Resend."""

    @abstractmethod
    def send(self, message: EmailMessage) -> str:
        """Send one email and return the provider's message ID."""
        raise NotImplementedError
