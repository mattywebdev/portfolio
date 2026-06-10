from django.contrib import admin

from .models import Project, Technology


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "featured", "display_order"]
    list_filter = ["status", "featured", "technologies"]
    search_fields = ["title", "description", "summary"]
    prepopulated_fields = {"slug": ["title"]}
    filter_horizontal = ["technologies"]