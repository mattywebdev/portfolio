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


FEATURE_TOOLTIPS = {
    "contact_form": "A simple contact page or form that sends enquiries to your inbox.",
    "booking_enquiry_form": "A structured form for bookings, quote requests, appointments, or project enquiries.",
    "image_gallery": "A tidy way to show photos, work examples, products, venues, or before-and-after images.",
    "testimonials": "A section for customer quotes, reviews, ratings, or trust signals.",
    "google_maps": "A map and location details so visitors can find your business or service area.",
    "blog_news": "An editable area for updates, articles, announcements, or SEO-friendly content.",
    "product_catalogue": "A browsable list of products or services without necessarily taking online payments.",
    "admin_editing": "A private admin area so you can edit selected content yourself after launch.",
    "login_accounts": "User accounts for customers, members, staff, or protected areas.",
    "payments": "Online payment flow using a provider such as Stripe, depending on the project scope.",
    "basic_seo": "Practical search basics like page titles, descriptions, clean URLs, and index-friendly structure.",
    "hosting_domain_help": "Help connecting the site to hosting, domain, DNS, email, or deployment setup.",
    "ongoing_maintenance": "Support after launch for updates, fixes, small improvements, or monitoring.",
}

CONTENT_STATUS_TOOLTIPS = {
    "logo_ready": "You already have a logo file or clear brand mark to use on the site.",
    "text_ready": "You have written page text, service descriptions, or copy that can be placed into the site.",
    "photos_ready": "You have usable photos, screenshots, team images, product images, or project photos.",
    "existing_website": "There is a current website I can review, reuse content from, or improve on.",
    "need_content_help": "You know the idea, but need help turning it into clear website wording.",
    "need_stock_images": "You do not have enough imagery yet and may need suitable stock images.",
    "need_guidance": "You are not sure what is ready yet and want help shaping the best next step.",
}


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
