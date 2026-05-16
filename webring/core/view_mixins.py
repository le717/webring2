from http import HTTPStatus

from django.http import HttpRequest, JsonResponse

from .auth import check_auth
from .tools import get_webring


__all__ = ["RequireAuthMixin"]


class RequireAuthMixin:
    """Require valid authorization to access the route."""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        is_authorized = check_auth(
            webring=get_webring(self.kwargs["ring"]), bearer=request.headers.get("Authorization")
        )
        if not is_authorized:
            return JsonResponse(
                {"message": "Unable to authorize request."},
                status=HTTPStatus.FORBIDDEN,
            )
        return super().dispatch(request, *args, **kwargs)
