from typing import Any

from django import template
from django.forms import BaseForm, BoundField
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_form_fields(form: BaseForm) -> str:
    rendered_values = [render_field(form[field]) for field in form.fields]
    return mark_safe("".join(rendered_values))


@register.simple_tag
def render_field(form_field: BoundField, **attrs: Any) -> str:
    render_function = {
        "select": render_select_input,
        "checkbox": render_checkbox_input,
    }.get(form_field.widget_type, render_text_input)
    return render_function(form_field, **attrs)


@register.simple_tag
def render_text_input(form_field: BoundField, **attrs: Any) -> str:
    TEXT_INPUT_TEMPLATE = """<div class="w-full mt-2" {% include "django/forms/attrs.html" %}>
      <label class="block mb-1 font-bold" for="{{ form_field.id_for_label }}">{{ form_field.label }}</label>
      {{ form_field }}
      <small class="pg-text-muted">{{ form_field.help_text|safe }}</small>
      {{ form_field.errors }}
    </div>
    """
    return _render_field(TEXT_INPUT_TEMPLATE, form_field, **attrs)


@register.simple_tag
def render_select_input(form_field: BoundField, **attrs: Any) -> str:
    SELECT_INPUT_TEMPLATE = """<div class="w-full mt-2" {% include "django/forms/attrs.html" %}>
      <label class="block mb-1 font-bold" for="{{ form_field.id_for_label }}">{{ form_field.label }}</label>
      {{ form_field }}
      <small class="pg-text-muted">{{ form_field.help_text|safe }}</small>
      {{ form_field.errors }}
    </div>
    """
    return _render_field(SELECT_INPUT_TEMPLATE, form_field, **attrs)


@register.simple_tag
def render_checkbox_input(form_field: BoundField, **attrs: Any) -> str:
    CHECKBOX_INPUT_TEMPLATE = """
    <div class="w-full mt-2" {% include "django/forms/attrs.html" %}>
      <div>
        <label class="font-bold cursor-pointer flex items-center gap-2">
          {{ form_field }}
          {{ form_field.label }}
        </label>
      </div>
      <small class="pg-text-muted">{{ form_field.help_text|safe }}</small>
      {{ form_field.errors }}
    </div>
    """
    return _render_field(CHECKBOX_INPUT_TEMPLATE, form_field, **attrs)


def _render_field(template_text: str, form_field: BoundField, **attrs: Any) -> str:
    if not form_field.is_hidden:
        template_object = template.Template(template_text)
    else:
        template_object = template.Template("{{ form_field }}")
    attrs = _transform_x_attrs(attrs)
    context = template.Context({"form_field": form_field, "attrs": attrs})
    return template_object.render(context)


def _transform_x_attrs(attrs: dict[str, Any]) -> dict[str, Any]:
    """
    No support for `@click` style attributes or `.` modifiers
    """

    def _make_x_attr(key: str) -> str:
        if key.startswith("x"):
            # support `x-bind:placeholder` style options
            key = key[1:].replace("__", ":")
            return f"x-{key}"
        return key

    return {_make_x_attr(key): value for key, value in attrs.items()}
