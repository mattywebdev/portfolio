from django.shortcuts import render

from .selectors import get_projects, get_skill_groups


def home(request):
    return render(
        request,
        "portfolio/home.html",
        {
            "projects": get_projects(),
            "skill_groups": get_skill_groups(),
        },
    )