# Job Search Log

A lightweight Django web app for tracking job applications throughout your job search. Log each opportunity, monitor its status, and keep notes and contacts all in one place.

## Features

- Track applications with status, work type, source, location, and key contacts
- Statuses: Exploring → Resume Submitted → Interview Scheduled → Offer Accepted / Offer Declined / Rejected
- Store both the job posting URL and a separate application status tracking URL
- Bulk import applications from CSV; export your full list to CSV at any time
- Django admin interface for power users

## Requirements

- Python 3.10+
- Django 6.0.3

## Setup

```bash
# Clone the repository
git clone https://github.com/your-username/JobSearchLog.git
cd JobSearchLog

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install django==6.0.3

# Apply database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

Then open http://localhost:8000/jobs/ in your browser.

## Configuration

| Environment variable | Purpose | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key — set this in production | Insecure dev key |

## CSV Import

Navigate to **Import CSV** from the job list. The file must include `company` and `title` columns. All other columns are optional:

| Column | Values |
|---|---|
| `status` | `exploring`, `resume_submitted` (default), `interview_scheduled`, `offer_accepted`, `offer_declined`, `rejected` |
| `work_type` | `on_site`, `hybrid`, `remote` |
| `source` | `linkedin`, `indeed`, `company_website`, `referral`, `recruiter`, `other` |
| `url` | Job posting URL |
| `application_status_url` | Application tracking/status portal URL |
| `date_applied` | YYYY-MM-DD |
| `office_location` | Free text |
| `key_contacts` | Free text |
| `notes` | Free text |

## Running Tests

```bash
python manage.py test jobtracker
```

## License

MIT — see [LICENSE](LICENSE).
