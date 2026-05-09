import json
from typing import Any
from urllib.parse import urljoin

from django.conf import settings
from django.views.generic import TemplateView

from ..core.tools import get_app_info


__all__ = ["EmbedView"]


class EmbedView(TemplateView):
    """Get a small JavaScript file that automatically embeds the requested webring on your site.

    Provide the appropriate query string arguments to filter the result set as desired.
    """

    template_name = "embed/embed.js"
    content_type = "text/javascript"
    http_method_names = ["head", "get"]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Provide the information needed to render an embeddable webring."""
        ctx: dict[str, Any] = super().get_context_data()

        # Respect any filtering arguments provided in the request, falling back
        # to app-level defaults if they are not provided
        ctx |= {
            "app": get_app_info(),
            "base_url": urljoin(
                self.request._current_scheme_host, self.request.resolver_match.kwargs["ring"]
            ),
            "slug": self.request.resolver_match.kwargs["ring"],
            "page": int(self.request.GET.get("page", 1)),
            "options": json.dumps({
                "include_dead": self.request.GET.get("include_dead", settings.FILTER_INCLUDE_DEAD),
                "include_origin": self.request.GET.get(
                    "include_origin", settings.FILTER_INCLUDE_ORIGIN
                ),
                "include_web_archive": self.request.GET.get(
                    "include_web_archive", settings.FILTER_INCLUDE_WEB_ARCHIVE
                ),
            }),
        }
        return ctx
