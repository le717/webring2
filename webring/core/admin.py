from django.contrib import admin
from django.http import HttpRequest
from django_softdelete.admin import GlobalObjectsModelAdmin

from ..linkrot.models import LinkrotHistory
from .models import Entry, Webring, WebringAPIKey


class WebringAPIKeyInline(admin.TabularInline):
    model = WebringAPIKey
    fields = ["api_key", "is_active"]
    # readonly_fields = ["date_added", "api_key"]
    extra = 0

    def get_readonly_fields(self, request: HttpRequest, obj) -> list[str]:
        return [*super().get_readonly_fields(request, obj), "api_key"]


@admin.register(Webring)
class WebringAdmin(GlobalObjectsModelAdmin):
    inlines = [WebringAPIKeyInline]
    list_display = [
        "name",
        "slug",
        "url",
        "author",
        "maintainer",
        "is_active",
        "is_deleted",
        "deleted_at",
    ]
    list_filter = ["is_active"]
    fields = ["name", "slug", "url", "author", "maintainer", "description", "is_active"]
    prepopulated_fields = {"slug": ["name"]}
    ordering = ["name", "is_active"]
    search_fields = ["name", "url", "author", "maintainer"]
    search_help_text = "Search by webring name, url, author, or maintainer."

    class Media:
        css = {"all": ("core/css/core-admin.css",)}


class LinkrotHistoryInline(admin.TabularInline):
    model = LinkrotHistory

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False


@admin.register(Entry)
class EntryAdmin(GlobalObjectsModelAdmin):
    inlines = [LinkrotHistoryInline]
    list_display = [
        "title",
        "url",
        "is_dead",
        "is_web_archive",
        "is_deleted",
        "deleted_at",
        "instance",
    ]
    fields = [
        "instance",
        "url",
        "title",
        "description",
        "is_dead",
        "is_web_archive",
        "uuid",
    ]
    readonly_fields = ["uuid"]
    autocomplete_fields = ["instance"]
    ordering = ["instance", "title"]
    search_fields = ["title", "description", "url"]
    search_help_text = "Search by entry title, description, or URL."

    class Media:
        css = {"all": ("core/css/core-admin.css",)}
