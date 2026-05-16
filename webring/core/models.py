from secrets import token_hex
from typing import Any
from uuid import uuid7

from django.db import models
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _
from django_softdelete.models import SoftDeleteModel


__all__ = ["Entry", "LinkrotHistory", "Webring"]


class Webring(SoftDeleteModel):
    """Represent a single webring instance."""

    class Meta:
        db_table_comment = _("Store the individual webring instances being run on this app.")

    def __str__(self) -> str:
        return f"{self.name} ({self.url})"

    def _asdict(self) -> dict[str, Any]:
        return {
            k: v
            for k, v in model_to_dict(self).items()
            if k in ["name", "url", "description", "author", "maintainer"]
        }

    name = models.CharField(max_length=512, help_text=_("The webring's name."))
    url = models.URLField(verbose_name="URL", help_text=_("The URL of the webring."))
    slug = models.SlugField(unique=True, help_text="The slug used to access this webring.")
    author = models.CharField(
        max_length=512, blank=True, default="", help_text=_("The primary author of the webring.")
    )
    maintainer = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text=_("The primary maintainer of the maintainer."),
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text=_(
            "A brief description of the webring's purpose or intention. Should be short(er)."
        ),
    )
    api_key = models.CharField(
        max_length=512,
        blank=True,
        default=token_hex,
        verbose_name="Admin API key",
        help_text="The admin API key for accessing protected routes.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicate if this webring is live, meaning it can be viewed and traversed.",
    )


class Entry(SoftDeleteModel):
    class Meta:
        verbose_name_plural = "Entries"
        db_table_comment = _("Store the entries for an individual webring.")

    def __str__(self) -> str:
        return self.title

    def _asdict(self) -> dict[str, Any]:
        # We must be careful to properly extract the datetime fields, as they are excluded
        # by `model_to_dict`
        return {
            k: getattr(self, k)
            for k in [f.name for f in self._meta.get_fields()]
            if k in ["title", "description", "url", "is_dead", "is_web_archive"]
        }

    uuid = models.UUIDField(
        unique=True,
        default=uuid7,
        verbose_name="UUID",
        help_text=_("A unique UUID for this entry. This is auto-generated and cannot be changed."),
    )
    title = models.CharField(max_length=2_048, help_text=_("The entry's title."))
    description = models.CharField(
        max_length=1_024,
        blank=True,
        default="",
        help_text=_("The entry's description. Should be short(er)."),
    )
    url = models.URLField(verbose_name="URL", help_text=_("The entry's URL."))
    date_added = models.DateTimeField(
        auto_now_add=True, help_text=_("The datetime this entry was added to the webring.")
    )
    date_last_updated = models.DateTimeField(
        auto_now=True,
        help_text=_(
            "The most recent datetime this entry was updated.",
        ),
    )
    is_dead = models.BooleanField(
        default=False,
        verbose_name="Entry is dead?",
        help_text=_("Indicate if this entry is dead (i.e., cannot be accessed anymore.)"),
    )
    is_web_archive = models.BooleanField(
        default=False,
        verbose_name="Entry redirects to Web Archive?",
        help_text=_("Indicate if this entry's URL is now pointed to The Web Archive."),
    )
    instance = models.ForeignKey(
        Webring,
        on_delete=models.CASCADE,
        related_name="entries",
        help_text=_("The webring this entry belong to."),
    )
