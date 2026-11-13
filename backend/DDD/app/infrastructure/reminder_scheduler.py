"""Run reminder scans in a background thread beside the FastAPI server."""

from apscheduler.schedulers.background import BackgroundScheduler

from app.application.reminder_service import ReminderRunResult, ReminderService
from app.logging import log_step


class ReminderScheduler:
    """What: Trigger the reminder use case while the API keeps serving requests.

    When: FastAPI starts and stops its application lifespan.
    How: APScheduler runs one interval job in a background thread.
    """

    def __init__(self, service: ReminderService, interval_seconds: int) -> None:
        self.service = service
        self.interval_seconds = interval_seconds
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self.scheduler.add_job(
            self._process_reminders,
            trigger="interval",
            seconds=interval_seconds,
            id="todoflow-reminder-scan",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=max(interval_seconds * 2, 60),
        )

    def start(self) -> None:
        """Process overdue reminders once, then start recurring scans."""
        # Startup scan server downtime mein due honay wali reminders recover karta hai.
        self._log_result(self.service.process_due())
        self.scheduler.start()
        log_step(
            "Setup",
            "Email reminder scheduler started with the API.",
            "Email reminder scheduler API ke sath start ho gaya.",
        )

    def shutdown(self) -> None:
        """Stop the background thread during FastAPI shutdown/reload."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            log_step(
                "Setup",
                "Email reminder scheduler stopped.",
                "Email reminder scheduler stop ho gaya.",
            )

    def _process_reminders(self) -> None:
        """Run one due-reminder batch without overlapping the previous batch."""
        self._log_result(self.service.process_due())

    @staticmethod
    def _log_result(result: ReminderRunResult) -> None:
        """Log useful scans without printing an empty message every interval."""
        if result.found or result.failed:
            log_step(
                "Reminder",
                f"Scan found {result.found}; sent {result.sent}; failed {result.failed}.",
                f"Scan mein {result.found} milay; {result.sent} send; {result.failed} fail.",
            )
