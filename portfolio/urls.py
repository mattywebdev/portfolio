from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "favicon.ico",
        RedirectView.as_view(url=static("portfolio/images/favicon.ico"), permanent=True),
        name="favicon",
    ),
    path("start-project/", views.start_project, name="start_project"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail")
]
