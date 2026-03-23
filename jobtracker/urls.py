from django.urls import path
from .views import JobListView, JobCreateView, JobUpdateView, JobDeleteView, job_export_csv, job_import_csv, job_activity_log

urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),
    path('add/', JobCreateView.as_view(), name='job_create'),
    path('<int:pk>/edit/', JobUpdateView.as_view(), name='job_update'),
    path('<int:pk>/delete/', JobDeleteView.as_view(), name='job_delete'),
    path('<int:pk>/activity/', job_activity_log, name='job_activity_log'),
    path('export/', job_export_csv, name='job_export_csv'),
    path('import/', job_import_csv, name='job_import_csv'),
]
