from celery import shared_task
from django.core.management import call_command


@shared_task
def clear_expired_sessions_task() -> None:
    """Clears stale expired sessions from the database."""
    call_command("clearsessions")
