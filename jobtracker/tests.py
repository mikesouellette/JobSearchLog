import io
from django.test import TestCase
from django.urls import reverse
from .models import Job


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
