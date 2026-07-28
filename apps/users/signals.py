from typing import Any

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed, user_signed_up
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import mail_admins
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.http import HttpRequest

from apps.users.models import CustomUser


@receiver(user_signed_up)
def handle_sign_up(request: HttpRequest, user: CustomUser, **kwargs: Any) -> None:
    # customize this function to do custom logic on sign up, e.g. send a welcome email
    # or subscribe them to your mailing list.
    # This example notifies the admins, in case you want to keep track of sign ups
    _notify_admins_of_signup(user)


@receiver(email_confirmed)
def update_user_email(sender: Any, request: HttpRequest, email_address: EmailAddress, **kwargs: Any) -> None:
    """
    When an email address is confirmed make it the primary email.
    """
    # This also sets user.email to the new email address.
    # hat tip: https://stackoverflow.com/a/29661871/8207
    email_address.set_as_primary()


def _notify_admins_of_signup(user: CustomUser) -> None:
    mail_admins(
        f"Yowsers, someone signed up for {settings.PROJECT_METADATA['NAME']}!",
        f"Email: {user.email}",
        fail_silently=True,
    )


@receiver(pre_save, sender=CustomUser)
def remove_old_profile_picture_on_change(sender: type[CustomUser], instance: CustomUser, **kwargs: Any) -> None:
    if not instance.pk:
        return

    try:
        old_file = sender.objects.get(pk=instance.pk).avatar
    except sender.DoesNotExist:
        return

    if old_file.name and old_file.name != instance.avatar.name and default_storage.exists(old_file.name):
        default_storage.delete(old_file.name)


@receiver(post_delete, sender=CustomUser)
def remove_profile_picture_on_delete(sender: type[CustomUser], instance: CustomUser, **kwargs: Any) -> None:
    if instance.avatar.name and default_storage.exists(instance.avatar.name):
        default_storage.delete(instance.avatar.name)
