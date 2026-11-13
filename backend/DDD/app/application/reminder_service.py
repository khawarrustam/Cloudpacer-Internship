"""Application use case for sending due todo reminder emails."""

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape

from app.domain.notification import EmailMessage, EmailSender
from app.domain.todo import TodoItem, TodoRepository
from app.logging import log_error, log_step


@dataclass(frozen=True)
class ReminderRunResult:
    """Small summary returned after one scheduler scan."""

    found: int
    sent: int
    failed: int


class ReminderService:
    """What: Find due reminders, send email, and persist delivery state.

    When: The API's background scheduler runs its recurring scan.
    How: Read through TodoRepository and send through the EmailSender port.
    """

    def __init__(
        self,
        repository: TodoRepository,
        email_sender: EmailSender,
        batch_size: int,
    ) -> None:
        self.repository = repository
        self.email_sender = email_sender
        self.batch_size = batch_size

    def process_due(self, now: datetime | None = None) -> ReminderRunResult:
        """Attempt every due reminder once and leave failures for a later retry."""
        current_time = now or datetime.now(timezone.utc)
        todos = self.repository.get_due_reminders(
            current_time,
            self.batch_size,
        )
        sent = 0
        failed = 0

        for todo in todos:
            if not todo.reminder_is_due(current_time):
                continue
            try:
                provider_id = self.email_sender.send(
                    self._build_message(todo)
                )
                # Sent state provider success ke baad save hoti hai. Same stable
                # idempotency key retry ke waqt duplicate Resend email rokti hai.
                todo.mark_reminder_sent(current_time)
                self.repository.save(todo)
                sent += 1
                log_step(
                    "Reminder",
                    f"Todo {todo.id} reminder sent as {provider_id}.",
                    f"Todo {todo.id} ka reminder send ho gaya.",
                )
            except Exception as error:
                failed += 1
                log_error("Reminder", f"Todo {todo.id} reminder failed: {error}")

        return ReminderRunResult(found=len(todos), sent=sent, failed=failed)

    @staticmethod
    def _build_message(todo: TodoItem) -> EmailMessage:
        """Create a safe branded email plus a plain-text fallback."""
        title = todo.title.value
        safe_title = escape(title)
        subject_title = " ".join(title.splitlines())
        priority = todo.priority.value.title()
        due_text = todo.reminder.due_at.strftime(
            "%A, %d %B %Y at %I:%M %p UTC"
        )
        reminder_stamp = int(todo.reminder.reminder_at.timestamp())
        priority_background, priority_color = {
            "High": ("#fef2f2", "#b91c1c"),
            "Medium": ("#fff7ed", "#c2410c"),
            "Low": ("#ecfdf5", "#047857"),
        }[priority]

        # Inline styles zyada email clients mein reliably render hoti hain.
        html = f"""<!doctype html>
<html lang="en">
  <body style="margin:0;background:#f3f5f9;font-family:Arial,sans-serif;color:#172033;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
           style="background:#f3f5f9;padding:40px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
                 style="max-width:600px;background:#ffffff;border:1px solid #e4e7ec;
                        border-radius:18px;overflow:hidden;box-shadow:0 10px 30px rgba(23,32,51,.08);">
            <tr>
              <td style="background:#3157d5;padding:22px 30px;color:#ffffff;">
                <span style="display:inline-block;width:30px;height:30px;line-height:30px;
                             margin-right:10px;border-radius:9px;background:#ffffff;color:#3157d5;
                             text-align:center;font-size:17px;font-weight:800;">✓</span>
                <span style="font-size:18px;font-weight:800;vertical-align:middle;">TodoFlow</span>
              </td>
            </tr>
            <tr>
              <td style="padding:34px 30px 30px;">
                <p style="margin:0 0 10px;color:#3157d5;font-size:12px;font-weight:800;
                          letter-spacing:1.2px;text-transform:uppercase;">Task reminder</p>
                <h1 style="margin:0;font-size:26px;line-height:1.3;color:#172033;">
                  Your task is due soon
                </h1>
                <p style="margin:12px 0 26px;color:#667085;font-size:15px;line-height:1.7;">
                  Here is a friendly reminder for your upcoming task.
                </p>

                <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
                       style="border:1px solid #e4e7ec;border-radius:14px;background:#fafbfc;">
                  <tr>
                    <td colspan="2" style="padding:22px 22px 18px;">
                      <p style="margin:0 0 7px;color:#98a2b3;font-size:11px;font-weight:800;
                                letter-spacing:1px;text-transform:uppercase;">Task</p>
                      <p style="margin:0;color:#172033;font-size:18px;font-weight:800;
                                line-height:1.5;">{safe_title}</p>
                    </td>
                  </tr>
                  <tr>
                    <td style="border-top:1px solid #e4e7ec;padding:18px 22px;">
                      <p style="margin:0 0 5px;color:#98a2b3;font-size:11px;font-weight:800;
                                text-transform:uppercase;">Due date</p>
                      <p style="margin:0;color:#344054;font-size:14px;font-weight:700;">
                        {escape(due_text)}
                      </p>
                    </td>
                    <td align="right" style="border-top:1px solid #e4e7ec;padding:18px 22px;">
                      <span style="display:inline-block;padding:7px 11px;border-radius:999px;
                                   background:{priority_background};color:{priority_color};
                                   font-size:11px;font-weight:800;text-transform:uppercase;">
                        {priority} priority
                      </span>
                    </td>
                  </tr>
                </table>

                <p style="margin:25px 0 0;color:#667085;font-size:14px;line-height:1.7;">
                  Open TodoFlow to review the task and mark it complete when you are done.
                </p>
              </td>
            </tr>
            <tr>
              <td style="border-top:1px solid #e4e7ec;background:#fafbfc;padding:18px 30px;
                         color:#98a2b3;font-size:12px;line-height:1.6;">
                This automated reminder was scheduled from your TodoFlow account.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

        return EmailMessage(
            recipient=todo.reminder.recipient_email or "",
            subject=f"Reminder: {subject_title} is due soon",
            text=(
                "TODOFLOW TASK REMINDER\n\n"
                f"Task: {title}\n"
                f"Due: {due_text}\n"
                f"Priority: {priority}\n\n"
                "Open TodoFlow to review the task and mark it complete."
            ),
            html=html,
            idempotency_key=f"todo-reminder/{todo.id}/{reminder_stamp}",
        )
