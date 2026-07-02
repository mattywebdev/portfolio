from django import forms
from django.contrib import admin

from .forms import CONTENT_STATUS_CHOICES, FEATURE_CHOICES
from .models import Project, ProjectEnquiry, Technology


def format_selected_choices(selected_values, choices):
    labels_by_value = dict(choices)
    selected_labels = [
        labels_by_value.get(value, value)
        for value in selected_values
    ]

    if not selected_labels:
        return "-"

    return ", ".join(selected_labels)


class ProjectEnquiryAdminForm(forms.ModelForm):
    features = forms.MultipleChoiceField(
        choices=FEATURE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    content_status = forms.MultipleChoiceField(
        choices=CONTENT_STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Content readiness",
    )

    class Meta:
        model = ProjectEnquiry
        fields = "__all__"


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
    form = ProjectEnquiryAdminForm
    list_display = [
        "client_name",
        "business_name",
        "project_type",
        "budget_range",
        "timeframe",
        "features_summary",
        "content_status_summary",
        "status",
        "created_at",
    ]
    list_filter = ["status", "project_type", "budget_range", "timeframe", "created_at"]
    search_fields = ["client_name", "business_name", "email", "current_website", "message"]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
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

    @admin.display(description="Features")
    def features_summary(self, obj):
        return format_selected_choices(obj.features, FEATURE_CHOICES)

    @admin.display(description="Content")
    def content_status_summary(self, obj):
        return format_selected_choices(obj.content_status, CONTENT_STATUS_CHOICES)
