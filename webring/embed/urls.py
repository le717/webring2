from django.urls import path

from . import views


app_name = "embed"
urlpatterns = [path("<slug:ring>/webring-embed.js", views.EmbedView.as_view(), name="js_embed")]
