from django.db import models
from django.urls import reverse


class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "technologies"

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ("live", "Live"),
        ("in_progress", "In progress"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField()
    technologies = models.ManyToManyField(Technology, related_name="projects")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress")
    url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    featured = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=140, unique=True, blank=True, null=True)
    summary = models.CharField(max_length=220, blank=True)
    image = models.ImageField(upload_to="projects/", blank=True)
    started_on = models.DateField(blank=True, null=True)
    completed_on = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=120, blank=True)
    problem = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    features = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    future_improvements = models.TextField(blank=True)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if not self.slug:
            return reverse("portfolio:home") + "#projects"

        return reverse("portfolio:project_detail", kwargs={"slug": self.slug})


class ProjectEnquiry(models.Model):
    PROJECT_TYPE_CHOICES = [
        ("new_business_website", "New business website"),
        ("website_redesign", "Website redesign"),
        ("landing_page", "Landing page"),
        ("portfolio_personal", "Portfolio or personal website"),
        ("booking_enquiry_form", "Website with booking/enquiry form"),
        ("product_catalogue", "Product/catalogue website"),
        ("custom_web_app", "Custom web application"),
        ("not_sure", "Not sure yet"),
    ]

    PAGES_NEEDED_CHOICES = [
        ("one_page", "1 page"),
        ("two_four", "2-4 pages"),
        ("five_eight", "5-8 pages"),
        ("nine_plus", "9+ pages"),
        ("not_sure", "Not sure"),
    ]

    BUDGET_RANGE_CHOICES = [
        ("under_300", "Under GBP 300"),
        ("300_500", "GBP 300-500"),
        ("500_1000", "GBP 500-1,000"),
        ("1000_plus", "GBP 1,000+"),
        ("not_sure", "Not sure yet"),
    ]

    TIMEFRAME_CHOICES = [
        ("asap", "ASAP"),
        ("one_two_weeks", "1-2 weeks"),
        ("two_four_weeks", "2-4 weeks"),
        ("flexible", "Flexible"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("reviewing", "Reviewing"),
        ("contacted", "Contacted"),
        ("quoted", "Quoted"),
        ("won", "Won"),
        ("lost", "Lost"),
        ("spam", "Spam"),
    ]

    project_type = models.CharField(max_length=80, choices=PROJECT_TYPE_CHOICES)
    pages_needed = models.CharField(max_length=40, choices=PAGES_NEEDED_CHOICES)
    features = models.JSONField(default=list, blank=True)
    content_status = models.JSONField(default=list, blank=True)
    budget_range = models.CharField(max_length=40, choices=BUDGET_RANGE_CHOICES, blank=True)
    timeframe = models.CharField(max_length=40, choices=TIMEFRAME_CHOICES, blank=True)
    client_name = models.CharField(max_length=120)
    business_name = models.CharField(max_length=160, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    current_website = models.URLField(blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "project enquiries"

    def __str__(self):
        return f"{self.client_name} - {self.get_project_type_display()}"


class ProjectEnquirySpamAttempt(models.Model):
    REASON_CHOICES = [
        ("honeypot", "Honeypot filled"),
        ("too_fast", "Submitted too quickly"),
        ("invalid_timestamp", "Invalid timestamp"),
    ]

    reason = models.CharField(max_length=40, choices=REASON_CHOICES)
    path = models.CharField(max_length=240, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=300, blank=True)
    submitted_email = models.EmailField(blank=True)
    submitted_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "blocked enquiry attempt"
        verbose_name_plural = "blocked enquiry attempts"

    def __str__(self):
        return f"{self.get_reason_display()} at {self.created_at:%Y-%m-%d %H:%M}"
