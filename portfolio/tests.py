import time
from unittest.mock import MagicMock, patch

from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from .forms import ProjectEnquiryForm
from .models import Project, ProjectEnquiry, ProjectEnquirySpamAttempt, Technology


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

    def test_home_page_links_to_privacy_policy(self):
        response = self.client.get(reverse("portfolio:home"))

        self.assertContains(response, reverse("portfolio:privacy_policy"))

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
        self.assertContains(response, "https://matty-dev.com/privacy/")
        self.assertContains(response, "https://matty-dev.com/projects/portfolio-site/")

    def test_privacy_policy_page_loads(self):
        response = self.client.get(reverse("portfolio:privacy_policy"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/privacy_policy.html")
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "Mateusz Obstawski")
        self.assertContains(response, "trading as")
        self.assertContains(response, "I do not publish my home address")
        self.assertContains(response, "Project enquiries are normally kept")
        self.assertContains(response, "Information Commissioner's Office")


class StartProjectPageTests(TestCase):
    def project_enquiry_data(self, **overrides):
        data = {
            "project_type": "new_business_website",
            "pages_needed": "two_four",
            "client_name": "Test Client",
            "email": "test@example.com",
            "website": "",
            "rendered_at": ProjectEnquiryForm.create_rendered_at_token(time.time() - 5),
        }
        data.update(overrides)

        return data

    def test_start_project_page_loads(self):
        response = self.client.get(reverse("portfolio:start_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/start_project.html")
        self.assertContains(response, "Send the project shape")
        self.assertContains(response, "Project shape")
        self.assertContains(response, "Local service website")
        self.assertContains(response, reverse("portfolio:privacy_policy"))
        self.assertContains(response, 'name="website"', html=False)
        self.assertContains(response, 'name="rendered_at"', html=False)

    def test_valid_project_enquiry_submission_creates_enquiry(self):
        response = self.client.post(
            reverse("portfolio:start_project"),
            self.project_enquiry_data(
                features=["contact_form", "basic_seo"],
                content_status=["logo_ready", "text_ready"],
                budget_range="500_1000",
                timeframe="two_four_weeks",
                business_name="Test Business",
                phone="00000000000",
                current_website="https://example.com",
                message="I need a clean business website.",
            ),
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
            self.project_enquiry_data(
                features=["contact_form", "basic_seo"],
                content_status=["logo_ready", "text_ready"],
                budget_range="500_1000",
                timeframe="two_four_weeks",
                business_name="Test & Business",
                phone="00000000000",
                current_website="https://example.com",
                message="I need a clean business website.",
            ),
        )

        self.assertRedirects(response, reverse("portfolio:start_project_thanks"))
        self.assertEqual(len(mail.outbox), 2)

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
        self.assertEqual(len(notification.alternatives), 1)
        self.assertIn("Review in Django admin", notification.alternatives[0].content)

        confirmation = mail.outbox[1]
        self.assertEqual(confirmation.to, ["test@example.com"])
        self.assertEqual(confirmation.reply_to, ["hello@matty-dev.com"])
        self.assertEqual(confirmation.subject, "Your project enquiry was received")
        self.assertIn("Hi Test Client,", confirmation.body)
        self.assertIn("Thanks for sending your project enquiry", confirmation.body)
        self.assertIn("Project: New business website", confirmation.body)
        self.assertEqual(len(confirmation.alternatives), 1)
        self.assertIn("Your project enquiry was received", confirmation.alternatives[0].content)

    @override_settings(
        EMAIL_BACKEND="portfolio.tests.FailingEmailBackend",
        PROJECT_ENQUIRY_NOTIFICATION_EMAIL="hello@matty-dev.com",
    )
    def test_project_enquiry_is_saved_when_notification_email_fails(self):
        with patch("portfolio.views.logger.exception") as mock_logger_exception:
            response = self.client.post(
                reverse("portfolio:start_project"),
                self.project_enquiry_data(),
            )

        self.assertRedirects(response, reverse("portfolio:start_project_thanks"))
        self.assertEqual(ProjectEnquiry.objects.count(), 1)
        self.assertEqual(mock_logger_exception.call_count, 2)

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
            self.project_enquiry_data(
                features=["contact_form"],
                content_status=["logo_ready"],
            ),
        )

        self.assertRedirects(response, reverse("portfolio:start_project_thanks"))
        self.assertEqual(mock_urlopen.call_count, 2)

        notification_request = mock_urlopen.call_args_list[0].args[0]
        self.assertEqual(notification_request.full_url, "https://api.resend.test/emails")
        self.assertEqual(notification_request.headers["Authorization"], "Bearer test-api-key")
        self.assertEqual(notification_request.headers["Accept"], "application/json")
        self.assertIn("MattyDevPortfolio", notification_request.headers["User-agent"])
        self.assertIn(b'"to": ["hello@matty-dev.com"]', notification_request.data)
        self.assertIn(b'"reply_to": "test@example.com"', notification_request.data)
        self.assertIn(b'"subject": "New project enquiry from Test Client"', notification_request.data)
        self.assertIn(b'"html":', notification_request.data)
        self.assertIn(b"Review in Django admin", notification_request.data)
        self.assertIn(b"Contact form", notification_request.data)
        self.assertIn(b"Review this enquiry", notification_request.data)

        confirmation_request = mock_urlopen.call_args_list[1].args[0]
        self.assertIn(b'"to": ["test@example.com"]', confirmation_request.data)
        self.assertIn(b'"reply_to": "hello@matty-dev.com"', confirmation_request.data)
        self.assertIn(b'"subject": "Your project enquiry was received"', confirmation_request.data)
        self.assertIn(b'"html":', confirmation_request.data)
        self.assertIn(b"Thanks for sending your project enquiry", confirmation_request.data)

    def test_invalid_project_enquiry_submission_does_not_create_enquiry(self):
        response = self.client.post(
            reverse("portfolio:start_project"),
            self.project_enquiry_data(
                project_type="new_business_website",
                pages_needed="two_four",
                email="not-an-email",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProjectEnquiry.objects.count(), 0)
        self.assertContains(response, "Some details need a quick check")
        self.assertContains(response, "Enter a valid email address.")

    def test_honeypot_submission_is_blocked_and_counted(self):
        response = self.client.post(
            reverse("portfolio:start_project"),
            self.project_enquiry_data(website="https://spam.example"),
            HTTP_USER_AGENT="SpamBot/1.0",
            REMOTE_ADDR="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProjectEnquiry.objects.count(), 0)
        self.assertEqual(ProjectEnquirySpamAttempt.objects.count(), 1)

        spam_attempt = ProjectEnquirySpamAttempt.objects.get()
        self.assertEqual(spam_attempt.reason, "honeypot")
        self.assertEqual(spam_attempt.submitted_email, "test@example.com")
        self.assertEqual(spam_attempt.user_agent, "SpamBot/1.0")

    def test_too_fast_submission_is_blocked_and_counted(self):
        response = self.client.post(
            reverse("portfolio:start_project"),
            self.project_enquiry_data(
                rendered_at=ProjectEnquiryForm.create_rendered_at_token()
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProjectEnquiry.objects.count(), 0)
        self.assertEqual(ProjectEnquirySpamAttempt.objects.count(), 1)
        self.assertEqual(ProjectEnquirySpamAttempt.objects.get().reason, "too_fast")

    def test_start_project_thanks_page_loads(self):
        response = self.client.get(reverse("portfolio:start_project_thanks"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/start_project_thanks.html")
        self.assertContains(response, "Your project enquiry has been sent.")
        self.assertContains(response, "Confirmation email sent")
        self.assertContains(response, "A copy of your enquiry should arrive at the email address you provided")
        self.assertNotContains(response, "data-email-toast")
        self.assertContains(response, '<meta name="robots" content="noindex,follow">')

    def test_start_project_thanks_page_shows_confirmation_email_once(self):
        session = self.client.session
        session["project_enquiry_confirmation_email"] = "client@example.com"
        session.save()

        response = self.client.get(reverse("portfolio:start_project_thanks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "client@example.com")
        self.assertContains(response, "A copy of your enquiry should arrive shortly")
        self.assertContains(response, "data-email-toast")
        self.assertContains(response, "Close confirmation message")
        self.assertNotIn("project_enquiry_confirmation_email", self.client.session)


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
