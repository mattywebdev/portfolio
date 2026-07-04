from django import forms

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
