from http import HTTPStatus

from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.template.response import TemplateResponse
from django.views.generic import ListView, View
from django_smart_ratelimit import rate_limit

from ..core.models import Entry
from ..core.tools import truthy_str_to_bool
from ..core.view_mixins import RequireAuthMixin
from .checking import check_all, check_one
from .models import LinkrotHistory


__all__ = ["LinkrotCheckAllView", "LinkrotCheckOneView", "LinkrotLinkHistoryView"]


class LinkrotCheckAllView(RequireAuthMixin, View):
    """Check an entire webring for rotting entries."""

    http_method_names = ["head", "post"]

    @rate_limit(key="ip", block=True)
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        # Optionally include previously marked dead entries in the ring-wide check
        include_dead = truthy_str_to_bool(request.GET.get("include_dead", False))
        return JsonResponse(
            {"results": check_all(self.kwargs["ring"], include_dead)}, status=HTTPStatus.OK
        )


class LinkrotCheckOneView(RequireAuthMixin, View):
    """Check a single entry in a webring for rotting."""

    http_method_names = ["head", "post"]

    @rate_limit(key="ip", block=True)
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            entry = Entry.objects.get(instance__slug=self.kwargs["ring"], uuid=self.kwargs["entry"])
            return JsonResponse({"results": [check_one(entry)]}, status=HTTPStatus.OK)
        except Entry.DoesNotExist:
            return JsonResponse(
                {"message": "That entry does not exist in the requested webring."},
                status=HTTPStatus.NOT_FOUND,
            )


class LinkrotLinkHistoryView(RequireAuthMixin, ListView):
    """View the linkrot checking results of a single entry."""

    http_method_names = ["head", "get"]
    model = LinkrotHistory
    ordering = "-date_added"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(
                entry__instance__slug=self.kwargs["ring"],
                entry__uuid=self.kwargs["entry"],
            )
        )

    @rate_limit(key="ip", rate="1/m", block=True)
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        # We do not have any history for this entry
        r: TemplateResponse = super().get(request, *args, **kwargs)
        history: QuerySet = r.context_data["object_list"]
        if not history:
            return JsonResponse(
                {"message": "Linkrot history is not available for this entry."},
                status=HTTPStatus.NOT_FOUND,
            )
        return JsonResponse({"history": [r._asdict() for r in history]}, status=HTTPStatus.OK)
