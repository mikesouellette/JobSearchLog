from django.db import models


class Job(models.Model):
    STATUS_CHOICES = [
        ('exploring', 'Exploring'),
        ('resume_submitted', 'Resume Submitted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
        ('rejected', 'Rejected'),
    ]
    WORK_TYPE_CHOICES = [
        ('on_site', 'On-site'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote'),
    ]
    SOURCE_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('indeed', 'Indeed'),
        ('company_website', 'Company Website'),
        ('referral', 'Referral'),
        ('recruiter', 'Recruiter'),
        ('other', 'Other'),
    ]

    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='resume_submitted')
    work_type = models.CharField(max_length=10, choices=WORK_TYPE_CHOICES, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, blank=True)
    url = models.URLField(blank=True)
    application_status_url = models.URLField(blank=True)
    date_applied = models.DateField(null=True, blank=True)
    office_location = models.CharField(max_length=200, blank=True)
    key_contacts = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} — {self.title}"


class Activity(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='activities')
    date = models.DateField()
    description = models.TextField()

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.date}: {self.description[:50]}"
