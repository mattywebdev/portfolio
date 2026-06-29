from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ProjectEnquiryForm
from .selectors import (
    get_about,
    get_profile_links,
    get_project_by_slug,
    get_projects,
    get_services,
    get_skill_groups,
)


def home(request):
    return render(
        request,
        "portfolio/home.html",
        {
            "about": get_about(),
            "profile_links": get_profile_links(),
            "projects": get_projects(),
            "services": get_services(),
            "skill_groups": get_skill_groups(),
        },
    )


def start_project(request):
    if request.method == "POST":
        form = ProjectEnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thanks - your project enquiry has been saved. I will review it and get back to you.",
            )
            return redirect("portfolio:start_project")
    else:
        form = ProjectEnquiryForm()

    return render(
        request,
        "portfolio/start_project.html",
        {
            "form": form,
            "profile_links": get_profile_links(),
        },
    )


def project_detail(request, slug):
    project = get_project_by_slug(slug)

    return render(
        request,
        "portfolio/project_detail.html",
        {
            "project": project,
            "profile_links": get_profile_links(),
        },
    )
