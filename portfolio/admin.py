from django import forms
from django.contrib import admin, messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from .forms import CONTENT_STATUS_CHOICES, FEATURE_CHOICES
from .models import Project, ProjectEnquiry, ProjectEnquirySpamAttempt, Technology


def format_selected_choices(selected_values, choices):
    labels_by_value = dict(choices)
    selected_labels = [
        labels_by_value.get(value, value)
        for value in selected_values
    ]

    if not selected_labels:
        return "-"

    return ", ".join(selected_labels)


STATUS_ACTION_LABELS = [
    ("reviewing", "Review"),
    ("contacted", "Contact"),
    ("quoted", "Quote"),
    ("won", "Win"),
    ("lost", "Lose"),
    ("spam", "Spam"),
]

STATUS_ACTIONS_BY_STATUS = {
    "new": ["reviewing", "spam"],
    "reviewing": ["contacted", "quoted", "lost", "spam"],
    "contacted": ["quoted", "won", "lost", "spam"],
    "quoted": ["won", "lost", "contacted"],
    "won": ["reviewing"],
    "lost": ["reviewing"],
    "spam": ["reviewing"],
}

STATUS_BADGE_STYLES = {
    "new": ("New", "#e0f2fe", "#075985"),
    "reviewing": ("Reviewing", "#fef3c7", "#92400e"),
    "contacted": ("Contacted", "#dbeafe", "#1d4ed8"),
    "quoted": ("Quoted", "#ede9fe", "#6d28d9"),
    "won": ("Won", "#dcfce7", "#166534"),
    "lost": ("Lost", "#fee2e2", "#991b1b"),
    "spam": ("Spam", "#f3f4f6", "#374151"),
}


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


def render_status_badge(status):
    label, background_color, text_color = STATUS_BADGE_STYLES.get(
        status,
        (status, "#f3f4f6", "#374151"),
    )

    return format_html(
        '<span style="display:inline-block; min-width:72px; padding:3px 8px; '
        'border-radius:999px; background:{}; color:{}; font-weight:600; '
        'text-align:center;">{}</span>',
        background_color,
        text_color,
        label,
    )


def get_status_action_label(current_status, next_status):
    if current_status in ["won", "lost", "spam"] and next_status == "reviewing":
        return "Reopen"

    return dict(STATUS_ACTION_LABELS)[next_status]


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
    actions = [
        "mark_as_reviewing",
        "mark_as_contacted",
        "mark_as_quoted",
        "mark_as_won",
        "mark_as_lost",
        "mark_as_spam",
    ]
    list_display = [
        "client_name",
        "business_name",
        "project_type",
        "budget_range",
        "timeframe",
        "features_summary",
        "content_status_summary",
        "status_badge",
        "status_actions",
        "created_at",
    ]
    list_filter = ["status", "project_type", "budget_range", "timeframe", "created_at"]
    search_fields = ["client_name", "business_name", "email", "current_website", "message"]
    readonly_fields = [
        "status_badge",
        "created_at",
        "updated_at",
    ]

    class Media:
        js = ("portfolio/js/project_enquiry_admin.js",)

    fieldsets = [
        (
            "Project",
            {
                "fields": [
                    "project_type",
                    "pages_needed",
                    "features",
                    "content_status",
                    ("budget_range", "timeframe"),
                ]
            },
        ),
        (
            "Contact",
            {
                "fields": [
                    "client_name",
                    "business_name",
                    ("email", "phone"),
                    "current_website",
                    "message",
                ]
            },
        ),
        (
            "Workflow",
            {
                "fields": [
                    "status_badge",
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

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        return render_status_badge(obj.status)

    @admin.display(description="Quick status")
    def status_actions(self, obj):
        action_links = []

        for status in STATUS_ACTIONS_BY_STATUS.get(obj.status, []):
            label = get_status_action_label(obj.status, status)

            url = reverse(
                "admin:portfolio_projectenquiry_set_status",
                args=[obj.pk, status],
            )
            action_links.append((url, status, label))

        if not action_links:
            return "-"

        return format_html_join(
            "",
            (
                '<a href="{}" data-status="{}" style="display:inline-block; margin:0 4px 4px 0; '
                'padding:3px 7px; border:1px solid #d1d5db; border-radius:4px; '
                'background:#f9fafb; color:#1f2937; font-weight:600; '
                'text-decoration:none;">{}</a>'
            ),
            action_links,
        )

    def get_urls(self):
        custom_urls = [
            path(
                "<int:object_id>/set-status/<str:status>/",
                self.admin_site.admin_view(self.set_status_view),
                name="portfolio_projectenquiry_set_status",
            ),
        ]

        return custom_urls + super().get_urls()

    def set_status_view(self, request, object_id, status):
        status_labels = dict(ProjectEnquiry.STATUS_CHOICES)

        if status not in status_labels:
            self.message_user(request, "That enquiry status is not valid.", messages.ERROR)
            return redirect("admin:portfolio_projectenquiry_changelist")

        enquiry = self.get_object(request, object_id)

        if enquiry is None:
            self.message_user(request, "That project enquiry could not be found.", messages.ERROR)
            return redirect("admin:portfolio_projectenquiry_changelist")

        enquiry.status = status
        enquiry.updated_at = timezone.now()
        enquiry.save(update_fields=["status", "updated_at"])

        if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "status": status,
                    "status_label": status_labels[status],
                    "status_badge_html": str(render_status_badge(status)),
                    "status_actions_html": str(self.status_actions(enquiry)),
                }
            )

        self.message_user(
            request,
            f"{enquiry.client_name} updated to {status_labels[status]}.",
        )

        return redirect("admin:portfolio_projectenquiry_changelist")

    def update_status(self, request, queryset, status):
        updated_count = queryset.update(status=status, updated_at=timezone.now())
        status_label = dict(ProjectEnquiry.STATUS_CHOICES)[status]
        self.message_user(
            request,
            f"{updated_count} project enquiry updated to {status_label}.",
        )

    @admin.action(description="Mark selected enquiries as reviewing")
    def mark_as_reviewing(self, request, queryset):
        self.update_status(request, queryset, "reviewing")

    @admin.action(description="Mark selected enquiries as contacted")
    def mark_as_contacted(self, request, queryset):
        self.update_status(request, queryset, "contacted")

    @admin.action(description="Mark selected enquiries as quoted")
    def mark_as_quoted(self, request, queryset):
        self.update_status(request, queryset, "quoted")

    @admin.action(description="Mark selected enquiries as won")
    def mark_as_won(self, request, queryset):
        self.update_status(request, queryset, "won")

    @admin.action(description="Mark selected enquiries as lost")
    def mark_as_lost(self, request, queryset):
        self.update_status(request, queryset, "lost")

    @admin.action(description="Mark selected enquiries as spam")
    def mark_as_spam(self, request, queryset):
        self.update_status(request, queryset, "spam")


@admin.register(ProjectEnquirySpamAttempt)
class ProjectEnquirySpamAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "reason",
        "submitted_email",
        "submitted_name",
        "ip_address",
    ]
    list_filter = ["reason", "created_at"]
    search_fields = ["submitted_email", "submitted_name", "ip_address", "user_agent"]
    readonly_fields = [
        "reason",
        "path",
        "ip_address",
        "user_agent",
        "submitted_email",
        "submitted_name",
        "created_at",
    ]
    ordering = ["-created_at"]
