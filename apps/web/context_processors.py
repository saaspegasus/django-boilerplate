from copy import copy
from typing import Any

from django.conf import settings
from django.http import HttpRequest

from .meta import absolute_url, get_server_root


def project_meta(request: HttpRequest) -> dict[str, Any]:
    # modify these values as needed and add whatever else you want globally available here
    project_data = copy(settings.PROJECT_METADATA)
    project_data["TITLE"] = "{} | {}".format(project_data["NAME"], project_data["DESCRIPTION"])
    return {
        "project_meta": project_data,
        "server_url": get_server_root(),
        "page_url": absolute_url(request.path),
        "page_title": "",
        "page_description": "",
        "page_image": "",
        "turnstile_key": getattr(settings, "TURNSTILE_KEY", None),
    }


def csrf_settings(request: HttpRequest) -> dict[str, str]:
    """
    Exposes the configured CSRF cookie name to templates so front-end JS can
    read the correct cookie regardless of how CSRF_COOKIE_NAME is set. See
    base.html (the <meta> tag) and assets/javascript/csrf.js.
    """
    return {
        "csrf_cookie_name": settings.CSRF_COOKIE_NAME,
    }


def google_analytics_id(request: HttpRequest) -> dict[str, str]:
    """
    Adds google analytics id to all requests
    """
    if settings.GOOGLE_ANALYTICS_ID:
        return {
            "GOOGLE_ANALYTICS_ID": settings.GOOGLE_ANALYTICS_ID,
        }
    else:
        return {}
