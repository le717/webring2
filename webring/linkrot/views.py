import dataclasses
from http import HTTPStatus

from django.http import HttpRequest, JsonResponse
from django.views.generic import View

from .models import LinkrotHistory


__all__ = ["LinkrotCheckAllView", "LinkrotCheckOneView", "LinkrotLinkHistoryView"]


@dataclasses.dataclass(slots=True, frozen=True)
class RotResult: ...


class LinkrotCheckAllView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse({}, status=HTTPStatus.OK)


class LinkrotCheckOneView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse({}, status=HTTPStatus.OK)


class LinkrotLinkHistoryView(View):
    """View the linkrot checking results of a single entry."""

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        # TODO: 404 is not workgin as expected
        try:
            history = LinkrotHistory.objects.filter(
                entry__instance__slug=kwargs["ring"], entry__uuid=kwargs["entry"]
            ).all()
        except LinkrotHistory.DoesNotExist:
            return JsonResponse(
                {"message": "Linkrot history is not available for this entry."},
                status=HTTPStatus.NOT_FOUND,
            )

        return JsonResponse({"history": [r._asdict() for r in history]}, status=HTTPStatus.OK)
