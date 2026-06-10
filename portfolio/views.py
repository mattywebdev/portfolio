from django.shortcuts import render

from .data import PROJECTS, SKILLS


def home(request):
    return render(
        request,
        "portfolio/home.html",
        {
            "projects": PROJECTS,
            "skills": SKILLS,
        },
    )