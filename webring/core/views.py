from http import HTTPStatus
from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views.generic import DetailView, ListView

from .models import Entry, Webring


__all__ = ["EntryView", "WebringListView"]


class WebringListView(ListView):
    model = Webring
    paginate_by = 15
    http_method_names = ["head", "get"]
    qs_filters = {
        "include_dead": True,
        "include_origin": False,
        "include_web_archive": True,
        "origin": "",
    }

    def get_queryset(self) -> QuerySet:
        filters: dict[str, bool] = {}
        qs = super().get_queryset().filter(slug=self.kwargs["ring"]).prefetch_related("entries")

        # Filter out the site in the entry we are on.
        # Make sure we normalize the casing of the two URLs to better ensure we filter correctly
        # TODO: check on case sensitivity with SQLite and if needed, impl the comment above
        if not self.qs_filters["include_origin"]:
            qs = qs.exclude(entries__url__iexact=self.qs_filters["origin"])

        # Filter out dead and/or Web Archive only links
        if not self.qs_filters["include_dead"]:
            filters["entries__is_dead"] = False
        if not self.qs_filters["include_web_archive"]:
            filters["entries__is_web_archive"] = False
        return qs.filter(**filters)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        # Respect any filtering arguments provided in the request
        self.qs_filters["include_origin"] = request.GET.get("include_origin", "no").lower() != "no"
        self.qs_filters["include_dead"] = request.GET.get("include_dead", "yes").lower() == "yes"
        self.qs_filters["include_web_archive"] = (
            request.GET.get("include_web_archive", "yes").lower() == "yes"
        )

        # Remove the site making the request from the result set if told to
        if not self.qs_filters["include_origin"]:
            self.qs_filters["origin"] = request.headers.get("Origin", "")

        # TODO: always return meta even if no entries
        # Handle not finding a webring by the given slug
        if not (qs := self.get_queryset()):
            return JsonResponse({}, status=HTTPStatus.NOT_FOUND)

        # Build up the response data
        obj = qs.get()
        entries = [entry._asdict() for entry in obj.entries.all()]
        return JsonResponse({"meta": obj._asdict(), "entries": entries}, status=HTTPStatus.OK)


class EntryView(DetailView):
    model = Entry
    # pk_url_kwarg = "webring"
