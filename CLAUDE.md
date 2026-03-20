# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server (http://localhost:8000/jobs/)
python manage.py runserver

# Run tests
python manage.py test jobtracker

# Run a single test
python manage.py test jobtracker.tests.JobListViewTest

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations
```

## Architecture

Django 6.0.3 MVT app with SQLite. Single app (`jobtracker`) inside the `JobSearchLog` project package.

**URL structure:**
- `/jobs/` — job list (home)
- `/jobs/new/` — create job
- `/jobs/<id>/edit/` — update job
- `/jobs/<id>/delete/` — delete job
- `/admin/` — Django admin

**Data model (`jobtracker/models.py`):** The `Job` model is the only model. Key fields: `company`, `title`, `status` (choice: resume_submitted/interview_scheduled/offer_accepted/offer_declined/rejected), `work_type` (on-site/hybrid/remote), `source` (LinkedIn/Indeed/Company Website/Referral/Recruiter/Other), `job_link`, `date_applied`, `office_location`, `key_contacts`, `notes`, `created_at`.

**Views (`jobtracker/views.py`):** All CRUD views are Django generic class-based views (`ListView`, `CreateView`, `UpdateView`, `DeleteView`).

**Forms (`jobtracker/forms.py`):** Single `JobForm` `ModelForm` with Bootstrap `form-control` widget classes applied.

**Templates:** `templates/base.html` provides Bootstrap 5.3.3 (CDN) layout; app templates in `templates/jobtracker/`.
