from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


__all__ = ["LinkrotHistory"]


class LinkrotHistory(models.Model):
    class Meta:
        verbose_name = "Entry history"
        verbose_name_plural = "Entry histories"
        db_table_comment = _("Audit log of linkrot checks.")

    def _asdict(self) -> dict[str, Any]:
        # We must be careful to properly extract the datetime fields, as they are excluded
        # by `model_to_dict`
        return {
            k: getattr(self, k)
            for k in [f.name for f in self._meta.get_fields()]
            if k in ["date_added", "url", "was_alive", "message"]
        }

    date_added = models.DateTimeField(
        auto_now_add=True, help_text=_("The datetime this check occurred.")
    )
    url = models.URLField(help_text=_("The URL checked."))
    was_alive = models.BooleanField(
        default=True,
        verbose_name="URL was alive?",
        help_text=_("Was the URL alive at the time of this check?"),
    )
    message = models.TextField(default="", help_text="Any message generated during the check.")
    entry = models.ForeignKey("core.Entry", on_delete=models.CASCADE, related_name="history")
