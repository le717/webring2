from django.urls import path

from . import views


app_name = "core"
urlpatterns = [
    path("<slug:slug>", views.WebringView.as_view(), name=""),
    # path("<uuid:webring>/<uuid:entry>", views.EntryView.as_view(), name=""),
    # path("/linkrot/", ...)
    # path("/webring-embed.js", ...)
]
