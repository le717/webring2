from .models import Webring


__all__ = ["check_auth"]


def extract_bearer_token(bearer: str, /) -> str | None:
    """Extract the API key from the Bearer token."""
    if not bearer.startswith("Bearer "):
        return None
    return split[1] if len(split := bearer.split(" ")) == 2 else None


def check_auth(*, webring: Webring | None, bearer: str | None) -> bool:
    """Determine if the given API key is authorized for the given webring."""
    # If we lack a webring or bearer token, we cannot figure out if we are authorized
    if webring is None or bearer is None:
        return False

    # Attempt to extract the API key
    if (token := extract_bearer_token(bearer)) is None:
        return False

    # Determine if the API key belongs to the requested webring and is active
    return webring.api_keys.filter(api_key=token, is_active=True).exists()
