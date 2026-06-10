from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
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