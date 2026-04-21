from typing import Any

from jinja2 import Environment


__all__ = ["environment"]


def environment(**options) -> dict[str, Any]:
    env = Environment(**options)
    return env
