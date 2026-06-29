from django.contrib import admin

from .models import Project, ProjectEnquiry, Technology


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "featured", "display_order", "url"]
    list_filter = ["status", "featured", "technologies"]
    search_fields = ["title", "description", "summary", "problem", "solution"]
    prepopulated_fields = {"slug": ["title"]}
    filter_horizontal = ["technologies"]
    fieldsets = [
        (
            "Overview",
            {
                "fields": [
                    "title",
                    "slug",
                    "summary",
                    "description",
                    "status",
                    "featured",
                    "display_order",
                    "role",
                ]
            },
        ),
        (
            "Links and media",
            {
                "fields": [
                    "url",
                    "source_url",
                    "image",
                    "started_on",
                    "completed_on",
                    "technologies",
                ]
            },
        ),
        (
            "Case study",
            {
                "fields": [
                    "problem",
                    "solution",
                    "features",
                    "lessons_learned",
                    "future_improvements",
                ]
            },
        ),
    ]


@admin.register(ProjectEnquiry)
class ProjectEnquiryAdmin(admin.ModelAdmin):
    list_display = [
        "client_name",
        "business_name",
        "project_type",
        "budget_range",
        "timeframe",
        "status",
        "created_at",
    ]
    list_filter = ["status", "project_type", "budget_range", "timeframe", "created_at"]
    search_fields = ["client_name", "business_name", "email", "current_website", "message"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (
            "Project",
            {
                "fields": [
                    "project_type",
                    "pages_needed",
                    "features",
                    "content_status",
                    "budget_range",
                    "timeframe",
                ]
            },
        ),
        (
            "Contact",
            {
                "fields": [
                    "client_name",
                    "business_name",
                    "email",
                    "phone",
                    "current_website",
                    "message",
                ]
            },
        ),
        (
            "Workflow",
            {
                "fields": [
                    "status",
                    "internal_notes",
                    "created_at",
                    "updated_at",
                ]
            },
        ),
    ]
