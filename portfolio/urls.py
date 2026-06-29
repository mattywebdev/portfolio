from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.home, name="home"),
    path("start-project/", views.start_project, name="start_project"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail")
]
