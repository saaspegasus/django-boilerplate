from pathlib import Path

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.base import FilterExpression, Node, Template
from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode, IncludeNode
from django.test import SimpleTestCase

TEMPLATE_DIR = Path(settings.BASE_DIR) / "templates"


class TemplateCompilationTests(SimpleTestCase):
    """Compiles every project template to catch errors that otherwise only show up when a page is rendered."""

    def test_templates_compile(self):
        for name in _template_names():
            with self.subTest(template=name):
                get_template(name)

    def test_extends_and_include_targets_exist(self):
        for name in _template_names():
            template = get_template(name).template
            for target in _static_template_references(template):
                with self.subTest(template=name, target=target):
                    try:
                        get_template(target)
                    except TemplateDoesNotExist:
                        self.fail(f"{name} references missing template {target}")


def _template_names() -> list[str]:
    return sorted(
        path.relative_to(TEMPLATE_DIR).as_posix()
        for path in TEMPLATE_DIR.rglob("*")
        if path.is_file() and path.suffix in {".html", ".txt"}
    )


def _static_template_references(template: Template) -> list[str]:
    """Names from {% extends %} and {% include %} tags that use a string literal rather than a variable."""
    references = []
    for node in template.nodelist.get_nodes_by_type(Node):
        if isinstance(node, ExtendsNode):
            expression = node.parent_name
        elif isinstance(node, IncludeNode):
            expression = node.template
        else:
            continue
        if isinstance(expression, FilterExpression) and isinstance(expression.var, str):
            references.append(expression.var)
    return references
