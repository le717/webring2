from http import HTTPStatus
from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views.generic import DetailView, ListView

from .models import Entry, Webring


__all__ = ["EntryView", "WebringListView"]


class WebringListView(ListView):
    model = Entry
    paginate_by = 15
    http_method_names = ("head", "get")
    qs_filters: dict[str, bool | str] = {"origin": ""}

    @staticmethod
    def truthy_str_to_bool(val: bool | str) -> bool:
        """Convert truthy strings to a Boolean value."""
        if isinstance(val, bool):
            return val
        return val.lower() in {"y", "yes", "t", "true", "o", "one", "1"}

    def get_webring(self) -> Webring | None:
        """Attempt to find a webring with the given slug."""
        return Webring.objects.filter(slug=self.kwargs["ring"]).first()

    def get_queryset(self) -> QuerySet:
        filters: dict[str, bool | str] = {}
        qs = super().get_queryset().filter(instance__slug=self.kwargs["ring"])

        # Filter out the site in the entry we are on. Make sure we normalize the casing of the two
        # URLs to better ensure we filter correctly. See Django docs on SQLite support
        # https://docs.djangoproject.com/en/6.0/ref/databases/#substring-matching-and-case-sensitivity
        if not self.qs_filters["include_origin"]:
            qs = qs.exclude(url=self.qs_filters["origin"].lower())

        # Filter out dead and/or Web Archive only links
        if not self.qs_filters["include_dead"]:
            filters["is_dead"] = False
        if not self.qs_filters["include_web_archive"]:
            filters["is_web_archive"] = False
        return qs.filter(**filters)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        # Respect any filtering arguments provided in the request, falling back
        # to app-level defaults if they are not provided
        self.qs_filters["include_origin"] = self.truthy_str_to_bool(
            request.GET.get("include_origin", settings.FILTER_INCLUDE_ORIGIN)
        )
        self.qs_filters["include_dead"] = self.truthy_str_to_bool(
            request.GET.get("include_dead", settings.FILTER_INCLUDE_DEAD)
        )
        self.qs_filters["include_web_archive"] = self.truthy_str_to_bool(
            request.GET.get("include_web_archive", settings.FILTER_INCLUDE_WEB_ARCHIVE)
        )

        # Remove the site making the request from the result set if told to
        if not self.qs_filters["include_origin"]:
            self.qs_filters["origin"] = request.headers.get("Origin", "")

        # Handle not finding a webring with the given slug
        if (webring := self.get_webring()) is None:
            return JsonResponse({}, status=HTTPStatus.NOT_FOUND)

        # Build up the response data, which includes not finding any entries in the given webring
        entries = [entry._asdict() for entry in self.get_queryset().all()]
        return JsonResponse({"meta": webring._asdict(), "entries": entries}, status=HTTPStatus.OK)


class EntryView(DetailView):
    model = Entry
    # pk_url_kwarg = "webring"
