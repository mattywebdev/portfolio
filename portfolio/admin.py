from django.contrib import admin

from .models import Project, Technology


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
