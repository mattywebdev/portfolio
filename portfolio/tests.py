from django.test import TestCase
from django.urls import reverse

from .models import Project, ProjectEnquiry, Technology


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        django = Technology.objects.create(name="Django")
        python = Technology.objects.create(name="Python")
        react = Technology.objects.create(name="React")
        vite = Technology.objects.create(name="Vite")

        affiliate_site = Project.objects.create(
            title="Affiliate Site",
            slug="affiliate-site",
            description="My affiliate website.",
            status="live",
            featured=True,
            display_order=1,
        )
        affiliate_site.technologies.add(django, python)

        portfolio_site = Project.objects.create(
            title="Portfolio Site",
            slug="portfolio-site",
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

    def test_project_detail_page_loads(self):
        response = self.client.get(
            reverse("portfolio:project_detail", kwargs={"slug": "portfolio-site"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portfolio Site")


class StartProjectPageTests(TestCase):
    def test_start_project_page_loads(self):
        response = self.client.get(reverse("portfolio:start_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/start_project.html")
        self.assertContains(response, "Send the project shape")

    def test_valid_project_enquiry_submission_creates_enquiry(self):
        response = self.client.post(
            reverse("portfolio:start_project"),
            {
                "project_type": "new_business_website",
                "pages_needed": "two_four",
                "features": ["contact_form", "basic_seo"],
                "content_status": ["logo_ready", "text_ready"],
                "budget_range": "500_1000",
                "timeframe": "two_four_weeks",
                "client_name": "Rafaello",
                "business_name": "Ronaldo",
                "email": "test@example.com",
                "phone": "00000000000",
                "current_website": "https://example.com",
                "message": "I need a clean business website.",
            },
        )

        self.assertRedirects(response, reverse("portfolio:start_project"))
        self.assertEqual(ProjectEnquiry.objects.count(), 1)

        enquiry = ProjectEnquiry.objects.get()
        self.assertEqual(enquiry.client_name, "Rafaello")
        self.assertEqual(enquiry.business_name, "Ronaldo")
        self.assertEqual(enquiry.features, ["contact_form", "basic_seo"])
        self.assertEqual(enquiry.content_status, ["logo_ready", "text_ready"])

    def test_invalid_project_enquiry_submission_does_not_create_enquiry(self):
        response = self.client.post(
            reverse("portfolio:start_project"),
            {
                "project_type": "new_business_website",
                "pages_needed": "two_four",
                "email": "not-an-email",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProjectEnquiry.objects.count(), 0)
        self.assertContains(response, "Enter a valid email address.")
