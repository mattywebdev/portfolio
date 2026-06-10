from django.shortcuts import get_object_or_404

from .data import ABOUT, PROFILE_LINKS, SERVICES, SKILL_GROUPS
from .models import Project


def get_projects():
    return [
        {
            "title": project.title,
            "description": project.summary or project.description,
            "tech": [tech.name for tech in project.technologies.all()],
            "status": project.get_status_display(),
            "detail_url": project.get_absolute_url(),
            "image_url": project.image.url if project.image else "",
            "url": project.url,
            "source_url": project.source_url,
        }
        for project in Project.objects.filter(featured=True).prefetch_related("technologies")
    ]


def get_skill_groups():
    return SKILL_GROUPS


def get_about():
    return ABOUT


def get_profile_links():
    return PROFILE_LINKS


def get_services():
    return SERVICES


def get_project_by_slug(slug):
    return get_object_or_404(
        Project.objects.prefetch_related("technologies"),
        slug=slug,
    )
