import dataclasses
from http import HTTPStatus
from typing import Any

from django.conf import settings
from django.core.paginator import Page
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, JsonResponse
from django.views.generic import CreateView, DetailView, ListView

from .models import Entry, Webring
from .tools import get_app_info, truthy_str_to_bool


__all__ = ["EntryView", "WebringListView"]


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class WebringListResponse:
    """Model a webring's list response."""

    meta: Webring | None
    page: Page | None = None
    entries: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    app: dict[str, str] = dataclasses.field(default_factory=get_app_info)

    def _asdict(self) -> dict:
        d = dataclasses.asdict(self)
        d["meta"] = d["meta"]._asdict() if d["meta"] else None

        # Build out pagination information
        d["page"] = (
            None
            if d["page"] is None
            else {
                "total_pages": d["page"].paginator.num_pages,
                "has_prev_page": d["page"].has_previous(),
                "has_next_page": d["page"].has_next(),
                "current_page": d["page"].number,
                "prev_page": d["page"].previous_page_number() if d["page"].has_previous() else None,
                "next_page": d["page"].next_page_number() if d["page"].has_next() else None,
            }
        )
        return d


class WebringListView(ListView):
    """Fetch all entries.

    Provide the appropriate query string arguments to filter the result set as desired.
    """

    model = Entry
    ordering = "title"
    paginate_by = settings.FILTER_ENTRIES_PER_PAGE
    http_method_names = ["head", "get"]
    qs_filters: dict[str, bool | str] = {"origin": ""}

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
        self.qs_filters["include_origin"] = truthy_str_to_bool(
            request.GET.get("include_origin", settings.FILTER_INCLUDE_ORIGIN)
        )
        self.qs_filters["include_dead"] = truthy_str_to_bool(
            request.GET.get("include_dead", settings.FILTER_INCLUDE_DEAD)
        )
        self.qs_filters["include_web_archive"] = truthy_str_to_bool(
            request.GET.get("include_web_archive", settings.FILTER_INCLUDE_WEB_ARCHIVE)
        )

        # Remove the site making the request from the result set if told to
        if not self.qs_filters["include_origin"]:
            self.qs_filters["origin"] = request.headers.get("Origin", "")

        # Handle not finding a webring with the given slug
        if (webring := self.get_webring()) is None:
            return JsonResponse(
                WebringListResponse(meta=None)._asdict(), status=HTTPStatus.NOT_FOUND
            )

        # Build up the response data, which includes not finding any entries in the given webring
        try:
            _, page, qs, _ = self.paginate_queryset(
                self.get_queryset().order_by(self.get_ordering()), self.paginate_by
            )

        # If there are no results to show, `paginate_queryset` raises a 404, which is why we catch
        # it instead of a `Pagination` exception like you might expect. This is effectively the same
        # response as not being able to locate a ring
        except Http404:
            # Construct a special page instance that allows navigation from an invalid page back to
            # the previous, valid page to occur
            page = Page(
                Entry.objects.none(),
                int(request.GET["page"][0]),
                self.paginator_class(Entry.objects.none(), 1),
            )
            return JsonResponse(
                WebringListResponse(meta=webring, page=page)._asdict(),
                status=HTTPStatus.NOT_FOUND,
            )

        entries = [entry._asdict() for entry in qs.all()]
        return JsonResponse(
            WebringListResponse(meta=webring, page=page, entries=entries)._asdict(),
            status=HTTPStatus.OK,
        )


class EntryCreateView(CreateView): ...


class EntryView(DetailView):
    model = Entry
    # pk_url_kwarg = "webring"
