from django.urls import path

from . import views


app_name = "linkrot"
urlpatterns = [
    path("<slug:ring>/", views.LinkrotCheckAllView.as_view(), name="check_all"),
    path("<slug:ring>/<uuid:entry>", views.LinkrotCheckOneView.as_view(), name="check_one"),
    path(
        "<slug:ring>/<uuid:entry>/history",
        views.LinkrotLinkHistoryView.as_view(),
        name="history",
    ),
]
