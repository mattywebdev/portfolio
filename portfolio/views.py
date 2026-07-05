import logging
import json
from urllib import request

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from .forms import CONTENT_STATUS_CHOICES, FEATURE_CHOICES, ProjectEnquiryForm
from .models import Project
from .selectors import (
    get_about,
    get_profile_links,
    get_project_by_slug,
    get_projects,
    get_services,
    get_skill_groups,
)


SITE_URL = "https://matty-dev.com"
logger = logging.getLogger(__name__)


def get_choice_labels(selected_values, choices):
    labels_by_value = dict(choices)

    return ", ".join(
        labels_by_value.get(value, value)
        for value in selected_values
    )


def send_project_enquiry_notification_with_resend(enquiry, message):
    if not settings.RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY is not configured.")

    payload = json.dumps(
        {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [settings.PROJECT_ENQUIRY_NOTIFICATION_EMAIL],
            "reply_to": enquiry.email,
            "subject": f"New project enquiry from {enquiry.client_name}",
            "text": message,
        }
    ).encode("utf-8")

    resend_request = request.Request(
        settings.RESEND_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(resend_request, timeout=settings.EMAIL_TIMEOUT) as response:
        if response.status >= 400:
            raise RuntimeError(f"Resend API returned status {response.status}.")


def send_project_enquiry_notification_with_smtp(enquiry, message):
    email = EmailMessage(
        subject=f"New project enquiry from {enquiry.client_name}",
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.PROJECT_ENQUIRY_NOTIFICATION_EMAIL],
        reply_to=[enquiry.email],
    )
    email.send(fail_silently=False)


def send_project_enquiry_notification(enquiry):
    message = render_to_string(
        "portfolio/emails/project_enquiry_notification.txt",
        {
            "enquiry": enquiry,
            "feature_labels": get_choice_labels(enquiry.features, FEATURE_CHOICES),
            "content_status_labels": get_choice_labels(
                enquiry.content_status,
                CONTENT_STATUS_CHOICES,
            ),
        },
    )

    if settings.EMAIL_PROVIDER.lower() == "resend":
        send_project_enquiry_notification_with_resend(enquiry, message)
        return

    send_project_enquiry_notification_with_smtp(enquiry, message)


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


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {SITE_URL}{reverse('portfolio:sitemap')}",
        "",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    urls = [
        {
            "loc": SITE_URL + reverse("portfolio:home"),
            "priority": "1.0",
            "changefreq": "weekly",
        },
        {
            "loc": SITE_URL + reverse("portfolio:start_project"),
            "priority": "0.8",
            "changefreq": "monthly",
        },
    ]

    for project in Project.objects.exclude(slug__isnull=True).exclude(slug=""):
        urls.append(
            {
                "loc": SITE_URL + project.get_absolute_url(),
                "priority": "0.7",
                "changefreq": "monthly",
            }
        )

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in urls:
        sitemap.extend(
            [
                "  <url>",
                f"    <loc>{url['loc']}</loc>",
                f"    <changefreq>{url['changefreq']}</changefreq>",
                f"    <priority>{url['priority']}</priority>",
                "  </url>",
            ]
        )

    sitemap.append("</urlset>")

    return HttpResponse("\n".join(sitemap), content_type="application/xml")


def start_project(request):
    if request.method == "POST":
        form = ProjectEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()

            try:
                send_project_enquiry_notification(enquiry)
            except Exception:
                logger.exception(
                    "Project enquiry notification email failed for enquiry %s.",
                    enquiry.pk,
                )

            return redirect("portfolio:start_project_thanks")
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


def start_project_thanks(request):
    return render(
        request,
        "portfolio/start_project_thanks.html",
        {
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
