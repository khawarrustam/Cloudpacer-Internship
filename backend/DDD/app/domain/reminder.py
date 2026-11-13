"""Todo reminder value object and scheduling business rules."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class ReminderError(Exception):
    """Parent error for reminder business-rule failures."""


class InvalidReminderError(ReminderError):
    """Raised when due/reminder dates cannot make a valid schedule."""


class ReminderAlreadySentError(ReminderError):
    """Raised when a sent reminder is marked as sent again."""


class ReminderOption(str, Enum):
    """Reminder choices exposed by the API and frontend."""

    NONE = "NONE"
    ONE_MINUTE = "1_MINUTE"
    ONE_HOUR = "1_HOUR"
    ONE_DAY = "1_DAY"
    THREE_DAYS = "3_DAYS"
    CUSTOM = "CUSTOM"


REMINDER_OFFSETS = {
    ReminderOption.ONE_MINUTE: timedelta(minutes=1),
    ReminderOption.ONE_HOUR: timedelta(hours=1),
    ReminderOption.ONE_DAY: timedelta(days=1),
    ReminderOption.THREE_DAYS: timedelta(days=3),
}


@dataclass
class ReminderSettings:
    """What: Keep one todo's due date and optional email reminder valid.

    When: A todo is created/restored or the scheduler sends its reminder.
    How: Normalize UTC dates, calculate offsets, and track one-time delivery.
    """

    due_at: datetime | None = None
    reminder_at: datetime | None = None
    recipient_email: str | None = None
    sent_at: datetime | None = None
    option: ReminderOption = ReminderOption.NONE

    @classmethod
    def create(
        cls,
        due_at: datetime | None,
        option: str,
        custom_reminder_at: datetime | None,
        recipient_email: str,
        now: datetime | None = None,
    ) -> "ReminderSettings":
        """Create valid reminder settings from the user's selected option."""
        current_time = _as_utc(now or datetime.now(timezone.utc))
        try:
            selected_option = ReminderOption(option.upper())
        except (AttributeError, ValueError) as error:
            raise InvalidReminderError("Select a valid reminder option.") from error

        if due_at is None:
            if selected_option is not ReminderOption.NONE:
                raise InvalidReminderError(
                    "Select a due date before adding a reminder."
                )
            return cls()

        clean_due_at = _as_utc(due_at)
        if clean_due_at <= current_time:
            raise InvalidReminderError("Due date must be in the future.")

        if selected_option is ReminderOption.NONE:
            return cls(due_at=clean_due_at)

        if not recipient_email.strip():
            raise InvalidReminderError("A reminder needs the account email.")

        if selected_option is ReminderOption.CUSTOM:
            if custom_reminder_at is None:
                raise InvalidReminderError("Select a custom reminder date and time.")
            reminder_at = _as_utc(custom_reminder_at)
        else:
            reminder_at = clean_due_at - REMINDER_OFFSETS[selected_option]

        if reminder_at >= clean_due_at:
            raise InvalidReminderError("Reminder must be before the due date.")
        if reminder_at <= current_time:
            raise InvalidReminderError(
                "Reminder time must be in the future; choose a later due date."
            )

        return cls(
            due_at=clean_due_at,
            reminder_at=reminder_at,
            recipient_email=recipient_email.strip().lower(),
            option=selected_option,
        )

    @classmethod
    def restore(
        cls,
        due_at: datetime | None,
        reminder_at: datetime | None,
        recipient_email: str | None,
        sent_at: datetime | None,
        option: str | None,
    ) -> "ReminderSettings":
        """Restore persisted settings without rejecting an old due date."""
        inferred_option = option or (
            ReminderOption.CUSTOM.value if reminder_at else ReminderOption.NONE.value
        )
        try:
            selected_option = ReminderOption(inferred_option)
        except ValueError as error:
            raise InvalidReminderError("Saved reminder option is invalid.") from error
        return cls(
            due_at=_as_utc(due_at) if due_at else None,
            reminder_at=_as_utc(reminder_at) if reminder_at else None,
            recipient_email=recipient_email,
            sent_at=_as_utc(sent_at) if sent_at else None,
            option=selected_option,
        )

    def is_due(self, now: datetime) -> bool:
        """Return true only for an unsent reminder whose time has arrived."""
        return bool(
            self.reminder_at
            and self.recipient_email
            and self.sent_at is None
            and self.reminder_at <= _as_utc(now)
        )

    def mark_sent(self, sent_at: datetime) -> None:
        """Record successful delivery once."""
        if self.sent_at is not None:
            raise ReminderAlreadySentError("Reminder email was already sent.")
        self.sent_at = _as_utc(sent_at)


def _as_utc(value: datetime) -> datetime:
    """Require timezone-aware input and normalize it to UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidReminderError("Dates must include a timezone.")
    return value.astimezone(timezone.utc)
