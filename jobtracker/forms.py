from django import forms
from .models import Job, Activity


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'company', 'title', 'status', 'work_type', 'source',
            'date_applied', 'office_location', 'url', 'application_status_url',
            'key_contacts', 'notes',
        ]
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'date_applied': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'office_location': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'application_status_url': forms.URLInput(attrs={'class': 'form-control'}),
            'key_contacts': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
