from django.urls import path

from . import views


app_name = "core"
urlpatterns = [
    # TODO: Can these be multiple routes or is it one single route with all of the individual methods?
    path("<slug:ring>/", views.WebringListView.as_view(), name="webring_list"),
    path("<slug:ring>/", views.EntryCreateView.as_view(), name="entry_create"),
    path("<slug:ring>/<uuid:entry>", views.EntryDeleteView.as_view(), name="entry_delete"),
    path("<slug:ring>/<uuid:entry>", views.EntryUpdateView.as_view(), name="entry_update"),
]
