import dataclasses
from http import HTTPStatus

from django.http import HttpRequest, JsonResponse
from django.views.generic import View


__all__ = ["LinkRotCheckAllView", "LinkRotCheckOneView", "LinkRotLinkHistoryView"]


@dataclasses.dataclass(slots=True, frozen=True)
class RotResult: ...


class LinkRotCheckAllView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse({}, status=HTTPStatus.OK)


class LinkRotCheckOneView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse({}, status=HTTPStatus.OK)


class LinkRotLinkHistoryView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse({}, status=HTTPStatus.OK)
