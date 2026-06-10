from django.db import models


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

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title