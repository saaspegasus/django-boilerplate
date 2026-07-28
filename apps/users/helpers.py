import os
from typing import TYPE_CHECKING, cast

from allauth.account import app_settings
from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext as _

if TYPE_CHECKING:
    from apps.users.models import CustomUser


def require_email_confirmation() -> bool:
    return settings.ACCOUNT_EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY


def user_has_confirmed_email_address(user: CustomUser, email: str) -> bool:
    try:
        email_obj = EmailAddress.objects.get_for_user(user, email)
        return email_obj.verified
    except EmailAddress.DoesNotExist:
        return False


def get_authenticated_user(request: HttpRequest) -> CustomUser:
    """
    Get the authenticated user, resolving API-key auth if needed.

    Callers must guarantee authentication (e.g. via permission classes or login_required).
    """
    if request.user.is_anonymous:
        raise ValueError("get_authenticated_user requires an authenticated user")
    else:
        return cast("CustomUser", request.user)


def validate_profile_picture(value) -> None:
    valid_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".tif",
        ".tiff",
        ".webp",
        ".bmp",
    }
    file_extension = os.path.splitext(value.name)[1].lower()
    if file_extension not in valid_extensions:
        raise ValidationError(
            _("Please upload a valid image file! Supported types are {types}").format(
                types=", ".join(valid_extensions),
            )
        )
    max_file_size = 5242880  # 5 MB limit
    if value.size > max_file_size:
        size_in_mb = value.size // 1024**2
        raise ValidationError(
            _("Maximum file size allowed is 5 MB. Provided file is {size} MB.").format(
                size=size_in_mb,
            )
        )
