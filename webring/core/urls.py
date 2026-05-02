from django.urls import path

from . import views


app_name = "core"
urlpatterns = [
    path("<slug:ring>/", views.WebringListView.as_view(), name="list"),
    path("<slug:ring>/<uuid:entry>", views.EntryView.as_view(), name="entry"),
]
