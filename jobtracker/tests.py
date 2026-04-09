import io
import json
import datetime
from django.test import TestCase
from django.urls import reverse
from .models import Job, Activity


class JobTrackerSmokeTest(TestCase):
    def setUp(self):
        self.job = Job.objects.create(
            company='Acme Corp',
            title='Software Engineer',
            status='resume_submitted',
        )

    def test_list_view(self):
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acme Corp')

    def test_create_view_get(self):
        response = self.client.get(reverse('job_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_view_post(self):
        response = self.client.post(reverse('job_create'), {
            'company': 'New Co',
            'title': 'Backend Dev',
            'status': 'resume_submitted',
            'work_type': '',
            'source': '',
            'url': '',
            'office_location': '',
            'key_contacts': '',
            'notes': '',
        })
        self.assertRedirects(response, reverse('job_list'))
        self.assertTrue(Job.objects.filter(company='New Co').exists())

    def test_update_view(self):
        response = self.client.post(
            reverse('job_update', args=[self.job.pk]),
            {
                'company': 'Acme Corp',
                'title': 'Senior Engineer',
                'status': 'interview_scheduled',
                'work_type': '',
                'source': '',
                'url': '',
                'office_location': '',
                'key_contacts': '',
                'notes': '',
            }
        )
        self.assertRedirects(response, reverse('job_list'))
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'interview_scheduled')

    def test_delete_view(self):
        response = self.client.post(reverse('job_delete', args=[self.job.pk]))
        self.assertRedirects(response, reverse('job_list'))
        self.assertFalse(Job.objects.filter(pk=self.job.pk).exists())


class CSVExportImportTest(TestCase):
    def setUp(self):
        self.job = Job.objects.create(
            company='Export Co',
            title='Data Analyst',
            status='resume_submitted',
            work_type='remote',
            source='linkedin',
        )

    def test_export_csv(self):
        response = self.client.get(reverse('job_export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode()
        self.assertIn('Export Co', content)
        self.assertIn('Data Analyst', content)

    def test_import_csv_valid(self):
        csv_content = (
            'company,title,status,work_type,source,url,date_applied,office_location,key_contacts,notes\n'
            'Import Corp,Engineer,resume_submitted,hybrid,indeed,,,,,\n'
        )
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = 'jobs.csv'
        response = self.client.post(reverse('job_import_csv'), {'csv_file': csv_file})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Job.objects.filter(company='Import Corp').exists())

    def test_import_csv_missing_required_fields(self):
        csv_content = 'company,title\n,No Title\n'
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = 'jobs.csv'
        response = self.client.post(reverse('job_import_csv'), {'csv_file': csv_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'skipped')


class ActivityLogTest(TestCase):
    def setUp(self):
        self.job = Job.objects.create(company='Acme', title='Engineer', status='exploring')
        self.activity = Activity.objects.create(
            job=self.job,
            date=datetime.date(2026, 3, 1),
            description='Submitted application',
        )

    def test_activity_log_get(self):
        response = self.client.get(reverse('job_activity_log', args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Submitted application')

    def test_activity_log_post(self):
        response = self.client.post(reverse('job_activity_log', args=[self.job.pk]), {
            'date': '2026-03-10',
            'description': 'Phone screen scheduled',
        })
        self.assertRedirects(response, reverse('job_activity_log', args=[self.job.pk]))
        self.assertEqual(self.job.activities.count(), 2)
        self.assertTrue(self.job.activities.filter(description='Phone screen scheduled').exists())

    def test_activity_log_ordering(self):
        Activity.objects.create(job=self.job, date=datetime.date(2026, 3, 15), description='Later entry')
        activities = list(self.job.activities.all())
        self.assertEqual(activities[0].description, 'Later entry')

class ApiCreateJobTest(TestCase):
    CREATE_URL = '/api/jobs/'

    def _post(self, payload):
        return self.client.post(
            self.CREATE_URL,
            json.dumps(payload),
            content_type='application/json',
        )

    def _valid_remote(self, **overrides):
        base = {'company': 'Acme', 'title': 'Engineer', 'work_type': 'remote', 'url': 'https://example.com/job'}
        base.update(overrides)
        return base

    def test_create_remote_job_returns_201(self):
        response = self._post(self._valid_remote())
        self.assertEqual(response.status_code, 201)

    def test_create_remote_job_persisted(self):
        self._post(self._valid_remote())
        self.assertTrue(Job.objects.filter(company='Acme', title='Engineer').exists())

    def test_status_auto_set_to_exploring(self):
        response = self._post(self._valid_remote())
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'exploring')
        self.assertEqual(Job.objects.get(pk=data['id']).status, 'exploring')

    def test_date_applied_auto_set_to_today(self):
        response = self._post(self._valid_remote())
        data = json.loads(response.content)
        self.assertEqual(data['date_applied'], datetime.date.today().isoformat())

    def test_create_onsite_job_with_location(self):
        payload = self._valid_remote(work_type='on_site', office_location='Austin, TX')
        response = self._post(payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['office_location'], 'Austin, TX')

    def test_create_hybrid_job_with_location(self):
        payload = self._valid_remote(work_type='hybrid', office_location='Chicago, IL')
        response = self._post(payload)
        self.assertEqual(response.status_code, 201)

    def test_missing_required_fields_returns_400(self):
        response = self._post({})
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.content)['errors']
        for field in ('company', 'title', 'work_type', 'url'):
            self.assertIn(field, errors)

    def test_missing_office_location_for_onsite_returns_400(self):
        response = self._post(self._valid_remote(work_type='on_site'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('office_location', json.loads(response.content)['errors'])

    def test_missing_office_location_for_hybrid_returns_400(self):
        response = self._post(self._valid_remote(work_type='hybrid'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('office_location', json.loads(response.content)['errors'])

    def test_invalid_work_type_returns_400(self):
        response = self._post(self._valid_remote(work_type='flying'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('work_type', json.loads(response.content)['errors'])

    def test_invalid_url_returns_400(self):
        response = self._post(self._valid_remote(url='not-a-url'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('url', json.loads(response.content)['errors'])

    def test_wrong_method_returns_405(self):
        response = self.client.get(self.CREATE_URL)
        self.assertEqual(response.status_code, 405)

    def test_invalid_json_returns_400(self):
        response = self.client.post(self.CREATE_URL, 'not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)


class ApiActiveJobsTest(TestCase):
    ACTIVE_URL = '/api/jobs/active/'

    def setUp(self):
        self.active = Job.objects.create(company='ActiveCo', title='Dev', status='exploring', url='https://a.com')
        Job.objects.create(company='DoneCo', title='Dev', status='offer_accepted', url='https://b.com')
        Job.objects.create(company='DeclinedCo', title='Dev', status='offer_declined', url='https://c.com')
        Job.objects.create(company='RejectedCo', title='Dev', status='rejected', url='https://d.com')

    def test_returns_200(self):
        response = self.client.get(self.ACTIVE_URL)
        self.assertEqual(response.status_code, 200)

    def test_excludes_inactive_statuses(self):
        response = self.client.get(self.ACTIVE_URL)
        jobs = json.loads(response.content)['jobs']
        companies = [j['company'] for j in jobs]
        self.assertIn('ActiveCo', companies)
        for inactive in ('DoneCo', 'DeclinedCo', 'RejectedCo'):
            self.assertNotIn(inactive, companies)

    def test_includes_all_active_statuses(self):
        Job.objects.create(company='ResumeCo', title='Dev', status='resume_submitted', url='https://e.com')
        Job.objects.create(company='InterviewCo', title='Dev', status='interview_scheduled', url='https://f.com')
        response = self.client.get(self.ACTIVE_URL)
        companies = [j['company'] for j in json.loads(response.content)['jobs']]
        for active in ('ActiveCo', 'ResumeCo', 'InterviewCo'):
            self.assertIn(active, companies)

    def test_response_shape(self):
        response = self.client.get(self.ACTIVE_URL)
        job = json.loads(response.content)['jobs'][0]
        self.assertEqual(set(job.keys()), {'id', 'company', 'title', 'url'})

    def test_all_inactive_returns_empty_list(self):
        Job.objects.filter(pk=self.active.pk).delete()
        response = self.client.get(self.ACTIVE_URL)
        self.assertEqual(json.loads(response.content)['jobs'], [])

    def test_wrong_method_returns_405(self):
        response = self.client.post(self.ACTIVE_URL)
        self.assertEqual(response.status_code, 405)
