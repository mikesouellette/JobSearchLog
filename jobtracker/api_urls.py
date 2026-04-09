from django.urls import path

from . import api_views

urlpatterns = [
    path('jobs/active/', api_views.active_jobs, name='api_job_active'),
    path('jobs/', api_views.create_job, name='api_job_create'),
]
