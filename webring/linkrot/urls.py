from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views


app_name = "linkrot"
urlpatterns = [
    path("<slug:ring>/", csrf_exempt(views.LinkrotCheckAllView.as_view()), name="check_all"),
    path(
        "<slug:ring>/<uuid:entry>/",
        csrf_exempt(views.LinkrotCheckOneView.as_view()),
        name="check_one",
    ),
    path(
        "<slug:ring>/<uuid:entry>/history",
        views.LinkrotLinkHistoryView.as_view(),
        name="history",
    ),
]
