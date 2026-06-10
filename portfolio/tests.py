from django.test import TestCase
from django.urls import reverse

from .models import Project, Technology


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        django = Technology.objects.create(name="Django")
        python = Technology.objects.create(name="Python")
        react = Technology.objects.create(name="React")
        vite = Technology.objects.create(name="Vite")

        affiliate_site = Project.objects.create(
            title="Affiliate Site",
            description="My affiliate website.",
            status="live",
            featured=True,
            display_order=1,
        )
        affiliate_site.technologies.add(django, python)

        portfolio_site = Project.objects.create(
            title="Portfolio Site",
            description="My portfolio website.",
            status="in_progress",
            featured=True,
            display_order=2,
        )
        portfolio_site.technologies.add(django, python, react, vite)

    def test_home_page_loads(self):
        response = self.client.get(reverse("portfolio:home"))

        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_template(self):
        response = self.client.get(reverse("portfolio:home"))

        self.assertTemplateUsed(response, "portfolio/home.html")

    def test_home_page_contains_project_content(self):
        response = self.client.get(reverse("portfolio:home"))

        self.assertContains(response, "Affiliate Site")
        self.assertContains(response, "Portfolio Site")

    def test_home_page_includes_projects_in_context(self):
        response = self.client.get(reverse("portfolio:home"))

        self.assertIn("projects", response.context)
        self.assertEqual(len(response.context["projects"]), 2)

    def test_home_page_includes_skill_groups_in_context(self):
        response = self.client.get(reverse("portfolio:home"))

        self.assertIn("skill_groups", response.context)
        self.assertEqual(len(response.context["skill_groups"]), 3)