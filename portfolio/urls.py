from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.home, name="home"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    path(
        "favicon.ico",
        RedirectView.as_view(url=static("portfolio/images/favicon.ico"), permanent=True),
        name="favicon",
    ),
    path("start-project/", views.start_project, name="start_project"),
    path("start-project/thanks/", views.start_project_thanks, name="start_project_thanks"),
    path("privacy/", views.privacy_policy, name="privacy_policy"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail")
]
