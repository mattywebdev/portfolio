from .data import SKILL_GROUPS
from .models import Project


def get_projects():
    return [
        {
            "title": project.title,
            "description": project.summary or project.description,
            "tech": [tech.name for tech in project.technologies.all()],
            "status": project.get_status_display(),
            "detail_url": project.get_absolute_url(),
            "url": project.url,
            "source_url": project.source_url,
        }
        for project in Project.objects.filter(featured=True).prefetch_related("technologies")
    ]


def get_skill_groups():
    return SKILL_GROUPS

def get_project_by_slug(slug):
    return Project.objects.prefetch_related("technologies").get(slug=slug)