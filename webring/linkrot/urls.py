from django.urls import path

from . import views


app_name = "linkrot"
urlpatterns = [
    # path("<slug:ring>/", views.WebringListView.as_view(), name="check_all"),
    # path("<slug:ring>/<uuid:entry>", views.EntryView.as_view(), name="check_one"),
    path(
        "<slug:ring>/<uuid:entry>/history",
        views.LinkrotLinkHistoryView.as_view(),
        name="history",
    ),
]
