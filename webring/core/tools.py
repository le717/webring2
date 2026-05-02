import tomllib
from pathlib import Path


__all__ = ["get_app_info"]


def get_app_info() -> dict[str, str]:
    """Provide basic webring2 application information for a response."""
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())
    return {
        "software": pyproject["project"]["urls"]["homepage"],
        "version": pyproject["project"]["version"],
    }
