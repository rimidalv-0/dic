import re

from jinja2 import Environment, FileSystemLoader

from . import state

_JINJA_SPECIAL_RE = re.compile(r"\{\{|\}\}|\{%|%\}|\{#|#\}")


def escape_literal_braces(text):
    return _JINJA_SPECIAL_RE.sub(lambda m: f"{{% raw %}}{m.group(0)}{{% endraw %}}", text)


def hex_to_rgb(value):
    value = value.lstrip("#")
    r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
    return f"{r}, {g}, {b}"


FILTERS = {
    "hex_to_rgb": hex_to_rgb,
}

_env = Environment(
    loader=FileSystemLoader(str(state.TEMPLATE_DIR)),
    keep_trailing_newline=True,
)
_env.filters.update(FILTERS)


def render_template(rel_path, data):
    template = _env.get_template(str(rel_path).replace("\\", "/"))
    return template.render(**data)
