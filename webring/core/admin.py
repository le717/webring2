from django.contrib import admin

from .models import Entry, History, Webring


@admin.register(Webring)
class WebringAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "author", "maintainer", "is_active"]
    list_filter = ["is_active"]
    readonly_fields = ["uuid"]
    ordering = ["name", "is_active"]
    search_fields = ["name", "url", "author", "maintainer"]
    search_help_text = "Search by webring name, url, author, or maintainer."


class EntryHistoryInline(admin.TabularInline):
    model = History

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    inlines = [EntryHistoryInline]
    list_display = ["title", "url", "is_dead", "is_web_archive", "instance"]
    fields = ["instance", "url", "title", "description", "is_dead", "is_web_archive"]
    search_fields = ["title", "description", "url"]
    readonly_fields = ["uuid"]
    autocomplete_fields = ["instance"]
    ordering = ["instance", "title"]
    search_help_text = "Search by entry title, description, or URL."


# @admin.register(History)
# class HistoryAdmin(admin.ModelAdmin):
#     def has_add_permission(self, *args, **kwargs) -> bool:
#         return False

#     def has_change_permission(self, *args, **kwargs) -> bool:
#         return False

#     def has_delete_permission(self, *args, **kwargs) -> bool:
#         return False
