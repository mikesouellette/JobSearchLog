import json
import datetime

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Job

INACTIVE_STATUSES = {'offer_accepted', 'offer_declined', 'rejected'}
VALID_WORK_TYPES = {c[0] for c in Job.WORK_TYPE_CHOICES}


@csrf_exempt
def create_job(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    errors = {}
    for field in ('company', 'title', 'work_type', 'url'):
        if not str(data.get(field, '')).strip():
            errors[field] = 'required'
    if errors:
        return JsonResponse({'errors': errors}, status=400)

    work_type = data['work_type'].strip()
    if work_type not in VALID_WORK_TYPES:
        return JsonResponse(
            {'errors': {'work_type': f'must be one of: {", ".join(sorted(VALID_WORK_TYPES))}'}},
            status=400,
        )

    if work_type in ('on_site', 'hybrid') and not data.get('office_location', '').strip():
        return JsonResponse(
            {'errors': {'office_location': 'required for on_site and hybrid roles'}},
            status=400,
        )

    try:
        URLValidator()(data['url'].strip())
    except ValidationError:
        return JsonResponse({'errors': {'url': 'enter a valid URL'}}, status=400)

    job = Job.objects.create(
        company=data['company'].strip(),
        title=data['title'].strip(),
        work_type=work_type,
        url=data['url'].strip(),
        office_location=data.get('office_location', '').strip(),
        status='exploring',
        date_applied=datetime.date.today(),
    )
    return JsonResponse({
        'id': job.pk,
        'company': job.company,
        'title': job.title,
        'work_type': job.work_type,
        'url': job.url,
        'office_location': job.office_location,
        'status': job.status,
        'date_applied': job.date_applied.isoformat(),
    }, status=201)


def active_jobs(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    jobs = Job.objects.exclude(status__in=INACTIVE_STATUSES).order_by('-created_at')
    return JsonResponse({
        'jobs': [
            {'id': j.pk, 'company': j.company, 'title': j.title, 'url': j.url}
            for j in jobs
        ]
    })
