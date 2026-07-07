import time

from django import forms
from django.core import signing
from django.core.exceptions import ValidationError

from .models import ProjectEnquiry


FEATURE_CHOICES = [
    ("contact_form", "Contact form"),
    ("booking_enquiry_form", "Booking/enquiry form"),
    ("image_gallery", "Image gallery"),
    ("testimonials", "Testimonials"),
    ("google_maps", "Google Maps"),
    ("blog_news", "Blog/news section"),
    ("product_catalogue", "Product catalogue"),
    ("admin_editing", "Admin editing"),
    ("login_accounts", "Login/accounts"),
    ("payments", "Payments"),
    ("basic_seo", "Basic SEO setup"),
    ("hosting_domain_help", "Hosting/domain help"),
    ("ongoing_maintenance", "Ongoing maintenance"),
]

CONTENT_STATUS_CHOICES = [
    ("logo_ready", "Logo ready"),
    ("text_ready", "Text/content ready"),
    ("photos_ready", "Photos ready"),
    ("existing_website", "Existing website available"),
    ("need_content_help", "Need help writing content"),
    ("need_stock_images", "Need stock images"),
    ("need_guidance", "Need guidance"),
]


class ProjectEnquiryForm(forms.ModelForm):
    MINIMUM_SUBMIT_SECONDS = 2
    RENDERED_AT_MAX_AGE_SECONDS = 60 * 60 * 2
    SPAM_ERROR_MESSAGE = "Unable to send this enquiry. Please refresh the page and try again."

    features = forms.MultipleChoiceField(
        choices=FEATURE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"aria-describedby": "features-help"}),
        required=False,
    )
    content_status = forms.MultipleChoiceField(
        choices=CONTENT_STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"aria-describedby": "content-status-help"}),
        required=False,
        label="Content readiness",
    )
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
        label="Leave this field blank",
    )
    rendered_at = forms.CharField(required=True, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.spam_block_reason = ""
        super().__init__(*args, **kwargs)

    @property
    def is_spam_blocked(self):
        return bool(self.spam_block_reason)

    def mark_spam_blocked(self, reason):
        if not self.spam_block_reason:
            self.spam_block_reason = reason

    @classmethod
    def create_rendered_at_token(cls, rendered_at=None):
        return signing.dumps(rendered_at or time.time(), salt="project-enquiry-rendered-at")

    def clean_website(self):
        value = self.cleaned_data.get("website", "")

        if value:
            self.mark_spam_blocked("honeypot")
            raise ValidationError(self.SPAM_ERROR_MESSAGE)

        return value

    def clean_rendered_at(self):
        token = self.cleaned_data.get("rendered_at")

        try:
            rendered_at = signing.loads(
                token,
                salt="project-enquiry-rendered-at",
                max_age=self.RENDERED_AT_MAX_AGE_SECONDS,
            )
        except signing.BadSignature as error:
            self.mark_spam_blocked("invalid_timestamp")
            raise ValidationError(self.SPAM_ERROR_MESSAGE) from error

        if time.time() - float(rendered_at) < self.MINIMUM_SUBMIT_SECONDS:
            self.mark_spam_blocked("too_fast")
            raise ValidationError(self.SPAM_ERROR_MESSAGE)

        return token

    class Meta:
        model = ProjectEnquiry
        fields = [
            "project_type",
            "pages_needed",
            "features",
            "content_status",
            "budget_range",
            "timeframe",
            "client_name",
            "business_name",
            "email",
            "phone",
            "current_website",
            "message",
        ]
        widgets = {
            "project_type": forms.Select(attrs={"aria-describedby": "project-type-help"}),
            "pages_needed": forms.Select(attrs={"aria-describedby": "pages-needed-help"}),
            "budget_range": forms.Select(attrs={"aria-describedby": "budget-range-help"}),
            "timeframe": forms.Select(attrs={"aria-describedby": "timeframe-help"}),
            "client_name": forms.TextInput(attrs={"aria-describedby": "client-name-help"}),
            "business_name": forms.TextInput(attrs={"aria-describedby": "business-name-help"}),
            "email": forms.EmailInput(attrs={"aria-describedby": "email-help"}),
            "phone": forms.TextInput(attrs={"aria-describedby": "phone-help"}),
            "current_website": forms.URLInput(attrs={"aria-describedby": "current-website-help"}),
            "message": forms.Textarea(attrs={"rows": 5, "aria-describedby": "message-help"}),
        }
