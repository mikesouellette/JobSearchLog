import csv
import io
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Job
from .forms import JobForm

CSV_FIELDS = ['company', 'title', 'status', 'work_type', 'source', 'url',
              'application_status_url', 'date_applied', 'office_location',
              'key_contacts', 'notes']


class JobListView(ListView):
    model = Job
    template_name = 'jobtracker/job_list.html'
    context_object_name = 'jobs'
    ordering = ['-created_at']


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
