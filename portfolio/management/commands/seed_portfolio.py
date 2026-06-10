from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File

from portfolio.models import Project, Technology


PROJECTS = [
    {
        "title": "Django Music Shop",
        "slug": "django-music-shop",
        "summary": "A full-stack Django e-commerce demo for browsing music, managing a cart, checking out, and using account features.",
        "description": (
            "Django Music Shop is a portfolio e-commerce application that simulates a real online store "
            "for albums, tracks, ambient releases, and merchandise."
        ),
        "status": "live",
        "url": "https://shop.matty-dev.com",
        "source_url": "https://github.com/mattywebdev/django-music-shop",
        "image": "portfolio/static/portfolio/images/projects/django-music-shop.png",
        "display_order": 1,
        "role": "Full-stack developer responsible for the Django backend, templates, shopping flow, REST endpoints, and deployment.",
        "problem": (
            "I wanted to build something more complete than a static catalog: a realistic store with carts, "
            "accounts, order history, API endpoints, and enough moving parts to practice how full-stack Django apps fit together."
        ),
        "solution": (
            "I built a Django shop with database-backed products, a session cart, checkout flow, user accounts, "
            "favorites, AJAX search suggestions, demo media, and Django REST Framework endpoints for albums, tracks, and search."
        ),
        "features": "Session-based cart\nCheckout with orders and order items\nUser registration, login, dashboard, and order history\nFavorites system\nAJAX search suggestions\nREST API endpoints\nDemo media and test coverage",
        "lessons_learned": (
            "This project helped me understand how e-commerce features depend on clean model relationships, "
            "reliable view logic, repeatable test coverage, and careful handling of user/session state."
        ),
        "future_improvements": "Payment provider integration\nStronger product management screens\nImproved API documentation\nProduction monitoring",
        "technologies": ["Django REST Framework", "AJAX", "Bootstrap", "Cart", "Accounts"],
    },
    {
        "title": "Affiliate Review Site",
        "slug": "affiliate-review-site",
        "summary": "A production Django affiliate review platform with articles, product listings, click tracking, analytics, and responsive pages.",
        "description": (
            "Affiliate Review Site is a Django product review platform focused on curated tech and gadget content, "
            "affiliate redirects, and admin-managed product/article data."
        ),
        "status": "live",
        "url": "https://affiliate.matty-dev.com",
        "source_url": "https://github.com/mattywebdev/affiliate-site",
        "image": "portfolio/static/portfolio/images/projects/affiliate-review-site.png",
        "display_order": 2,
        "role": "Full-stack developer responsible for product/article models, Django views, templates, click analytics, and VPS deployment.",
        "problem": (
            "Affiliate sites need more than product cards. They need structured content, category navigation, "
            "tracked outbound clicks, readable reviews, responsive pages, and a backend that can be updated without editing templates."
        ),
        "solution": (
            "I built a Django review platform with product categories, article pages, star ratings, pros and cons, "
            "affiliate redirects, click analytics, dynamic homepage sections, and production deployment on a Linux VPS."
        ),
        "features": "Article and buying-guide system\nProduct catalog with categories\nRatings with half-star support\nPros and cons\nAffiliate click tracking and redirects\nAnalytics panel\nResponsive custom CSS\nGunicorn/Nginx deployment",
        "lessons_learned": (
            "This project pushed me into more production-minded Django work: slugs, admin workflows, analytics, "
            "static/media handling, and running an app behind Gunicorn and Nginx."
        ),
        "future_improvements": "Add product comparison tools\nImprove SEO metadata and sitemap\nExplore PostgreSQL migration",
        "technologies": ["Click tracking", "Analytics", "Articles", "Ratings", "Linux VPS"],
    },
    {
        "title": "Willow & Thorn Florist Demo",
        "slug": "willow-thorn-florist-demo",
        "summary": "A polished Django small-business website demo for a florist, with bouquet filtering, dynamic content, and VPS deployment.",
        "description": (
            "Willow & Thorn is a realistic small-business demo site designed to show how Django can support local-business websites."
        ),
        "status": "live",
        "url": "https://florist.matty-dev.com",
        "source_url": "https://github.com/mattywebdev/willow-thorn-florist-demo",
        "image": "portfolio/static/portfolio/images/projects/willow-thorn-florist-demo.png",
        "display_order": 3,
        "role": "Full-stack developer responsible for the Django app, responsive frontend, admin-managed bouquets, image handling, and deployment.",
        "problem": (
            "Small businesses need websites that are attractive, easy to update, responsive on mobile, and deployable on real domains."
        ),
        "solution": (
            "I built a florist demo with database-driven bouquet content, category filtering, AJAX sorting, a featured carousel, "
            "WebP-optimized images, and production deployment with HTTPS."
        ),
        "features": "Responsive business homepage\nBouquet categories and filtering\nAJAX-powered sorting\nFeatured product carousel\nDjango admin content management\nWebP image optimization\nHTTPS custom domain deployment",
        "lessons_learned": (
            "This project helped me practice building a more client-facing website: visual polish, admin usability, "
            "image optimization, and the full path from local Django app to deployed VPS site."
        ),
        "future_improvements": "Online ordering\nDelivery scheduling\nCustomer accounts\nPayment integration\nCMS-style page editing",
        "technologies": ["AJAX", "Image optimization", "Admin content", "Nginx", "Gunicorn"],
    },
    {
        "title": "Portfolio Site",
        "slug": "portfolio-site",
        "summary": "This portfolio: a Django site with admin-managed projects, case-study pages, and a small React project filter.",
        "description": (
            "My portfolio site is built as a real Django project rather than a static page, with project data managed through the admin."
        ),
        "status": "in_progress",
        "url": "",
        "source_url": "",
        "image": "portfolio/static/portfolio/images/projects/portfolio-site.png",
        "display_order": 4,
        "role": "Full-stack developer building the site, data model, admin workflow, templates, styling, and React island.",
        "problem": (
            "I needed a portfolio that could grow with my projects without hardcoding every new project directly into templates."
        ),
        "solution": (
            "I built a Django-backed portfolio with Project and Technology models, admin editing, slug-based project pages, "
            "grouped skills, and a small React filter for the homepage project cards."
        ),
        "features": "Django admin-managed projects\nProject detail pages\nTechnology filtering with React\nGrouped skill sections\nReusable templates\nLocal Git workflow",
        "lessons_learned": (
            "This project is helping me connect Django fundamentals with a cleaner portfolio workflow: models, migrations, "
            "selectors, templates, frontend bundling, and deployment planning."
        ),
        "future_improvements": "GitHub repository setup\nVPS deployment\nScreenshots for each project\nBetter SEO metadata\nAutomated deployment",
        "technologies": ["Basic React", "Vite", "Admin content", "Case studies", "SQLite"],
    },
]


class Command(BaseCommand):
    help = "Seed portfolio projects and technologies for local development."

    def handle(self, *args, **options):
        seeded_slugs = []

        for source_project_data in PROJECTS:
            project_data = source_project_data.copy()
            technology_names = project_data.pop("technologies")
            image_path = project_data.pop("image")
            seeded_slugs.append(project_data["slug"])
            project, _created = Project.objects.update_or_create(
                slug=project_data["slug"],
                defaults={**project_data, "featured": True},
            )

            image_source_path = settings.BASE_DIR / image_path
            should_seed_image = (
                not project.image
                or project.image.name.startswith("portfolio/images/")
            )
            if image_source_path.exists() and should_seed_image:
                with image_source_path.open("rb") as image_file:
                    project.image.save(image_source_path.name, File(image_file), save=True)

            technologies = [
                Technology.objects.get_or_create(name=name)[0]
                for name in technology_names
            ]
            project.technologies.set(technologies)

        Project.objects.exclude(slug__in=seeded_slugs).update(featured=False)

        self.stdout.write(self.style.SUCCESS("Seeded portfolio projects."))
