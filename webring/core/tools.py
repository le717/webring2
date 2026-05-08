import tomllib
from pathlib import Path


__all__ = ["get_app_info", "truthy_str_to_bool"]


def get_app_info() -> dict[str, str]:
    """Provide basic webring2 application information for a response."""
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())
    return {
        "software": pyproject["project"]["urls"]["homepage"],
        "version": pyproject["project"]["version"],
    }


def truthy_str_to_bool(val: bool | str | None) -> bool:
    """Convert truthy strings to a Boolean value."""
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    return val.lower() in {"y", "yes", "t", "true", "o", "one", "1"}
