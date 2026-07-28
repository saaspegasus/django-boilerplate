from typing import Any

from django import template
from django.conf import settings
from django.templatetags.static import static

from apps.web import meta

register = template.Library()


@register.filter
def get_title(project_meta: dict[str, Any], page_title: str | None = None) -> str:
    if page_title:
        return "{} | {}".format(page_title, project_meta["NAME"])
    else:
        return project_meta["TITLE"]


@register.filter
def get_description(project_meta: dict[str, Any], page_description: str | None = None) -> str:
    return page_description or project_meta["DESCRIPTION"]


@register.filter
def get_image_url(project_meta: dict[str, Any], page_image: str | None = None) -> str:
    image = page_image or project_meta["IMAGE"]
    if not image:
        return ""
    if image.startswith(("http://", "https://")):
        return image
    # local media urls become absolute; anything else is treated as a static path
    if image.startswith(settings.MEDIA_URL):
        return meta.absolute_url(image)
    return meta.absolute_url(static(image))


@register.simple_tag
def absolute_url(path: str) -> str:
    return meta.absolute_url(path)
