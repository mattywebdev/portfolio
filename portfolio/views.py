from django.shortcuts import render

from .selectors import get_projects, get_skill_groups, get_project_by_slug


def home(request):
    return render(
        request,
        "portfolio/home.html",
        {
            "projects": get_projects(),
            "skill_groups": get_skill_groups(),
        },
    )

def project_detail(request, slug):
    project = get_project_by_slug(slug)

    return render(
        request,
        "portfolio/project_detail.html",
        {
            "project": project,
        },
    )