from typing import Any

from django.views.generic import TemplateView

from ..core.tools import get_app_info


__all__ = ["EmbedView"]


class EmbedView(TemplateView):
    """Get a small JavaScript file that automatically embeds the requested webring on your site.

    Provide the appropriate query string arguments to filter the result set as desired.

    # TODO: Effectively all of the processing from `WebringListView` needs to occur here, too
    """

    template_name = "embed/embed.js"
    content_type = "text/javascript"
    http_method_names = ["head", "get"]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Provide the information needed to render an embeddable webring."""
        ctx = super().get_context_data()
        ctx["entries"] = []
        ctx["config"] = get_app_info()
        return ctx
