from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from apps.users.models import CustomUser


class Command(BaseCommand):
    help = "Promotes the given user to a superuser and provides admin access."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("username", type=str)

    def handle(self, username: str, **options: Any) -> None:
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise CommandError(f"No user with username/email {username} found!") from None
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"{username} successfully promoted to superuser and can now access the admin site")
