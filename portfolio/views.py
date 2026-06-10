from django.shortcuts import render

from .data import PROJECTS, SKILL_GROUPS


def home(request):
    return render(
        request,
        "portfolio/home.html",
        {
            "projects": PROJECTS,
            "skill_groups": SKILL_GROUPS,
        },
    )