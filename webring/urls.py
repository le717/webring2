from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("embed/", include("webring.embed.urls", namespace="embed")),
    path("linkrot/", include("webring.linkrot.urls", namespace="linkrot")),
    path("", include("webring.core.urls", namespace="core")),
]

# TODO: http404 page
