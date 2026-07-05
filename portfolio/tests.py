from unittest.mock import MagicMock, patch

from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from .models import Project, ProjectEnquiry, Technology


class FailingEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise RuntimeError("Email backend failed")


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

    def test_robots_txt_loads(self):
        response = self.client.get(reverse("portfolio:robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "User-agent: *")
        self.assertContains(response, "Sitemap: https://matty-dev.com/sitemap.xml")

    def test_sitemap_xml_loads(self):
        response = self.client.get(reverse("portfolio:sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        self.assertContains(response, "https://matty-dev.com/")
        self.assertContains(response, "https://matty-dev.com/start-project/")
        self.assertContains(response, "https://matty-dev.com/projects/portfolio-site/")


class StartProjectPageTests(TestCase):
    def test_start_project_page_loads(self):
        response = self.client.get(reverse("portfolio:start_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/start_project.html")
        self.assertContains(response, "Send the project shape")
        self.assertContains(response, "Project shape")
        self.assertContains(response, "Local service website")

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
                "client_name": "Test Client",
                "business_name": "Test Business",
                "email": "test@example.com",
                "phone": "00000000000",
                "current_website": "https://example.com",
                "message": "I need a clean business website.",
            },
        )

        self.assertRedirects(response, reverse("portfolio:start_project_thanks"))
        self.assertEqual(ProjectEnquiry.objects.count(), 1)

        enquiry = ProjectEnquiry.objects.get()
        self.assertEqual(enquiry.client_name, "Test Client")
        self.assertEqual(enquiry.business_name, "Test Business")
        self.assertEqual(enquiry.features, ["contact_form", "basic_seo"])
        self.assertEqual(enquiry.content_status, ["logo_ready", "text_ready"])

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="Matty Dev <hello@matty-dev.com>",
        PROJECT_ENQUIRY_NOTIFICATION_EMAIL="hello@matty-dev.com",
    )
    def test_valid_project_enquiry_submission_sends_notification_email(self):
        response = self.client.post(
            reverse("portfolio:start_project"),
            {
                "project_type": "new_business_website",
                "pages_needed": "two_four",
                "features": ["contact_form", "basic_seo"],
                "content_status": ["logo_ready", "text_ready"],
                "budget_range": "500_1000",
                "timeframe": "two_four_weeks",
                "client_name": "Test Client",
                "business_name": "Test & Business",
                "email": "test@example.com",
                "phone": "00000000000",
                "current_website": "https://example.com",
                "message": "I need a clean business website.",
            },
        )

        self.assertRedirects(response, reverse("portfolio:start_project_thanks"))
        self.assertEqual(len(mail.outbox), 1)

        notification = mail.outbox[0]
        self.assertEqual(notification.to, ["hello@matty-dev.com"])
        self.assertEqual(notification.reply_to, ["test@example.com"])
        self.assertIn("New project enquiry from Test Client", notification.subject)
        self.assertIn("Quick summary", notification.body)
        self.assertIn("Business: Test & Business", notification.body)
        self.assertNotIn("Test &amp; Business", notification.body)
        self.assertIn("Contact form, Basic SEO setup", notification.body)
        self.assertIn("Logo ready, Text/content ready", notification.body)
        self.assertIn("/admin/portfolio/projectenquiry/", notification.body)

    @override_settings(
        EMAIL_BACKEND="portfolio.tests.FailingEmailBackend",
        PROJECT_ENQUIRY_NOTIFICATION_EMAIL="hello@matty-dev.com",
    )
    def test_project_enquiry_is_saved_when_notification_email_fails(self):
        response = self.client.post(
            reverse("portfolio:start_project"),
            {
                "project_type": "new_business_website",
                "pages_needed": "two_four",
                "client_name": "Test Client",
                "email": "test@example.com",
            },
        )

        self.assertRedirects(response, reverse("portfolio:start_project_thanks"))
        self.assertEqual(ProjectEnquiry.objects.count(), 1)

    @override_settings(
        EMAIL_PROVIDER="resend",
        RESEND_API_KEY="test-api-key",
        RESEND_API_URL="https://api.resend.test/emails",
        DEFAULT_FROM_EMAIL="Matty Dev <hello@matty-dev.com>",
        PROJECT_ENQUIRY_NOTIFICATION_EMAIL="hello@matty-dev.com",
        EMAIL_TIMEOUT=10,
    )
    @patch("portfolio.views.request.urlopen")
    def test_valid_project_enquiry_submission_sends_resend_notification(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        response = self.client.post(
            reverse("portfolio:start_project"),
            {
                "project_type": "new_business_website",
                "pages_needed": "two_four",
                "features": ["contact_form"],
                "content_status": ["logo_ready"],
                "client_name": "Test Client",
                "email": "test@example.com",
            },
        )

        self.assertRedirects(response, reverse("portfolio:start_project_thanks"))
        mock_urlopen.assert_called_once()

        resend_request = mock_urlopen.call_args.args[0]
        self.assertEqual(resend_request.full_url, "https://api.resend.test/emails")
        self.assertEqual(resend_request.headers["Authorization"], "Bearer test-api-key")
        self.assertEqual(resend_request.headers["Accept"], "application/json")
        self.assertIn("MattyDevPortfolio", resend_request.headers["User-agent"])
        self.assertIn(b'"reply_to": "test@example.com"', resend_request.data)
        self.assertIn(b'"subject": "New project enquiry from Test Client"', resend_request.data)
        self.assertIn(b"Contact form", resend_request.data)
        self.assertIn(b"Review this enquiry", resend_request.data)

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
        self.assertContains(response, "Some details need a quick check")
        self.assertContains(response, "Enter a valid email address.")

    def test_start_project_thanks_page_loads(self):
        response = self.client.get(reverse("portfolio:start_project_thanks"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/start_project_thanks.html")
        self.assertContains(response, "Your project enquiry has been sent.")
        self.assertContains(response, '<meta name="robots" content="noindex,follow">')


class ProjectEnquiryAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        self.client.force_login(self.admin_user)

    def test_project_enquiry_admin_list_loads(self):
        ProjectEnquiry.objects.create(
            project_type="new_business_website",
            pages_needed="two_four",
            features=["contact_form", "basic_seo"],
            content_status=["logo_ready"],
            budget_range="500_1000",
            timeframe="two_four_weeks",
            client_name="Test Client",
            business_name="Test Business",
            email="test@example.com",
        )

        response = self.client.get(reverse("admin:portfolio_projectenquiry_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contact form, Basic SEO setup")
        self.assertContains(response, "background:#e0f2fe")
        self.assertContains(response, "color:#075985")
        self.assertContains(response, ">New</span>")
        self.assertContains(response, "Review")
        self.assertContains(response, "Spam")
        self.assertNotContains(response, "Win")

    def test_project_enquiry_quick_status_endpoint_updates_status(self):
        enquiry = ProjectEnquiry.objects.create(
            project_type="new_business_website",
            pages_needed="two_four",
            features=["contact_form"],
            content_status=["logo_ready"],
            budget_range="500_1000",
            timeframe="two_four_weeks",
            client_name="Test Client",
            business_name="Test Business",
            email="test@example.com",
        )

        response = self.client.post(
            reverse(
                "admin:portfolio_projectenquiry_set_status",
                args=[enquiry.pk, "reviewing"],
            ),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        enquiry.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "reviewing")
        self.assertIn("Reviewing", response.json()["status_badge_html"])
        self.assertIn("Contact", response.json()["status_actions_html"])
        self.assertNotIn("Review", response.json()["status_actions_html"])
        self.assertEqual(enquiry.status, "reviewing")

    def test_project_enquiry_admin_list_shows_reopen_action_for_final_status(self):
        ProjectEnquiry.objects.create(
            project_type="new_business_website",
            pages_needed="two_four",
            features=["contact_form"],
            content_status=["logo_ready"],
            budget_range="500_1000",
            timeframe="two_four_weeks",
            client_name="Won Client",
            business_name="Won Business",
            email="won@example.com",
            status="won",
        )

        response = self.client.get(reverse("admin:portfolio_projectenquiry_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">Won</span>")
        self.assertContains(response, ">Reopen</a>")
        self.assertContains(response, 'data-status="reviewing"')
        self.assertNotContains(response, 'data-status="won"')
        self.assertNotContains(response, 'data-status="spam"')

    def test_project_enquiry_admin_change_page_loads(self):
        enquiry = ProjectEnquiry.objects.create(
            project_type="new_business_website",
            pages_needed="two_four",
            features=["contact_form"],
            content_status=["logo_ready"],
            budget_range="500_1000",
            timeframe="two_four_weeks",
            client_name="Detail Client",
            business_name="Detail Business",
            email="detail@example.com",
        )

        response = self.client.get(
            reverse("admin:portfolio_projectenquiry_change", args=[enquiry.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status:")
        self.assertContains(response, ">New</span>")
