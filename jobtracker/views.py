import csv
import io
import json
from collections import defaultdict
from datetime import date, timedelta
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Job, Activity
from .forms import JobForm, ActivityForm

CSV_FIELDS = ['company', 'title', 'status', 'work_type', 'source', 'url',
              'application_status_url', 'date_applied', 'office_location',
              'key_contacts', 'notes']


class JobListView(ListView):
    model = Job
    template_name = 'jobtracker/job_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        qs = Job.objects.order_by('-created_at')
        if self.request.GET.get('show_all') != '1':
            qs = qs.exclude(status__in=['rejected', 'offer_declined'])
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_all'] = self.request.GET.get('show_all') == '1'
        return context


class JobCreateView(CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobtracker/job_form.html'
    success_url = reverse_lazy('job_list')


class JobUpdateView(UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobtracker/job_form.html'
    success_url = reverse_lazy('job_list')


class JobDeleteView(DeleteView):
    model = Job
    template_name = 'jobtracker/job_confirm_delete.html'
    success_url = reverse_lazy('job_list')


def job_activity_log(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.job = job
            activity.save()
            return redirect('job_activity_log', pk=pk)
    else:
        form = ActivityForm()
    return render(request, 'jobtracker/job_activity_log.html', {
        'job': job,
        'activities': job.activities.all(),
        'form': form,
    })


def analytics(request):
    status_display = dict(Job.STATUS_CHOICES)
    status_colors = {
        'exploring': '#0d6efd',
        'resume_submitted': '#fd7e14',
        'interview_scheduled': '#ffc107',
        'offer_accepted': '#198754',
        'offer_declined': '#6c757d',
        'rejected': '#dc3545',
    }

    status_counts = (
        Job.objects.values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )
    status_labels = []
    status_data = []
    status_bg_colors = []
    for item in status_counts:
        status_labels.append(status_display.get(item['status'], item['status']))
        status_data.append(item['count'])
        status_bg_colors.append(status_colors.get(item['status'], '#adb5bd'))

    weeks_back = 12
    today = date.today()
    start_date = today - timedelta(weeks=weeks_back)
    start_date = start_date - timedelta(days=start_date.weekday())

    applied_dates = Job.objects.filter(
        date_applied__gte=start_date
    ).values_list('date_applied', flat=True)

    weekly_counts = defaultdict(int)
    for d in applied_dates:
        if d:
            week_start = d - timedelta(days=d.weekday())
            weekly_counts[week_start] += 1

    week_labels = []
    week_data = []
    for i in range(weeks_back):
        week_start = start_date + timedelta(weeks=i)
        week_labels.append(week_start.strftime('%b %-d'))
        week_data.append(weekly_counts.get(week_start, 0))

    return render(request, 'jobtracker/analytics.html', {
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'status_bg_colors': json.dumps(status_bg_colors),
        'week_labels': json.dumps(week_labels),
        'week_data': json.dumps(week_data),
        'total_jobs': Job.objects.count(),
    })


def job_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="jobs.csv"'
    writer = csv.DictWriter(response, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for job in Job.objects.all().order_by('-created_at'):
        writer.writerow({f: getattr(job, f) or '' for f in CSV_FIELDS})
    return response


def job_import_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            return render(request, 'jobtracker/job_import.html', {'error': 'Please upload a valid .csv file.'})

        valid_statuses = {c[0] for c in Job.STATUS_CHOICES}
        valid_work_types = {c[0] for c in Job.WORK_TYPE_CHOICES}
        valid_sources = {c[0] for c in Job.SOURCE_CHOICES}

        reader = csv.DictReader(io.TextIOWrapper(csv_file, encoding='utf-8'))
        imported = 0
        errors = []
        for i, row in enumerate(reader, start=2):  # row 1 is header
            company = row.get('company', '').strip()
            title = row.get('title', '').strip()
            if not company or not title:
                errors.append(f"Row {i}: 'company' and 'title' are required.")
                continue

            status = row.get('status', '').strip() or 'resume_submitted'
            if status not in valid_statuses:
                errors.append(f"Row {i}: invalid status '{status}'.")
                continue

            work_type = row.get('work_type', '').strip()
            if work_type and work_type not in valid_work_types:
                errors.append(f"Row {i}: invalid work_type '{work_type}'.")
                continue

            source = row.get('source', '').strip()
            if source and source not in valid_sources:
                errors.append(f"Row {i}: invalid source '{source}'.")
                continue

            date_applied = row.get('date_applied', '').strip() or None

            Job.objects.create(
                company=company,
                title=title,
                status=status,
                work_type=work_type,
                source=source,
                url=row.get('url', '').strip(),
                application_status_url=row.get('application_status_url', '').strip(),
                date_applied=date_applied,
                office_location=row.get('office_location', '').strip(),
                key_contacts=row.get('key_contacts', '').strip(),
                notes=row.get('notes', '').strip(),
            )
            imported += 1

        return render(request, 'jobtracker/job_import.html', {'imported': imported, 'errors': errors})

    return render(request, 'jobtracker/job_import.html')
