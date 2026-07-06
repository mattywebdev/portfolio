# Matty Dev Portfolio

Personal portfolio and small-business lead funnel for [matty-dev.com](https://matty-dev.com/).

This Django project presents selected web development work, project case studies, local service positioning, and a guided "start a project" enquiry flow. It is built as a real deployed portfolio rather than a static resume page.

## Current Features

- Django portfolio pages with project detail/case study routes.
- React-powered project filtering built with Vite.
- Admin-managed projects, technologies, screenshots, links, and case study content.
- Guided project enquiry form for website and web app leads.
- Project enquiry admin workflow with quick status actions.
- Responsive CSS layout for desktop and mobile.
- SEO basics including metadata, Open Graph tags, `robots.txt`, and `sitemap.xml`.
- Automated Django tests for core pages, enquiry flow, admin workflow, sitemap, and robots output.

## Tech Stack

- Python
- Django
- SQLite for local development
- JavaScript
- React
- Vite
- HTML and CSS

## Useful Commands

Run Django tests:

```powershell
py manage.py test
```

Build frontend assets:

```powershell
npm run build
```

Run the Vite dev server:

```powershell
npm run dev
```

Run the Django development server:

```powershell
py manage.py runserver
```

## Deployment Notes

Production for `matty-dev.com` runs from `/var/www/portfolio` on the VPS.
The Django app is managed by `portfolio.service`, not the older shared
`gunicorn.service` used by another site.

After pulling changes on the VPS:

```bash
cd /var/www/portfolio
git pull origin main
python manage.py collectstatic --noinput
sudo systemctl restart portfolio
```

Use `collectstatic` whenever CSS, JavaScript, images, or other static assets
change. Template-only and Python-only changes still need a `portfolio` restart.

Project enquiry emails use Resend in production because outbound SMTP is blocked
from the VPS. Real credentials live only in the ignored `.env` file:

```text
EMAIL_PROVIDER=resend
RESEND_API_KEY=...
RESEND_API_URL=https://api.resend.com/emails
DEFAULT_FROM_EMAIL=Matty Dev Website <website@matty-dev.com>
PROJECT_ENQUIRY_NOTIFICATION_EMAIL=hello@matty-dev.com
```

## Project Status

The portfolio is deployed and actively being improved. The current focus is polishing the project enquiry flow into a practical client intake experience.

## License

Copyright (c) 2026 Mateusz Obstawski. All rights reserved.

This project is publicly visible for portfolio and review purposes only. No permission is granted to copy, modify, redistribute, or use this code commercially without written permission.
