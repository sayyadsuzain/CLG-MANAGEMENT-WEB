import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Create the Celery app
app = Celery('backend')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered Django app configs
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configure Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'check-assignment-reminders': {
        'task': 'courses.tasks.check_assignment_reminders',
        'schedule': 3600.0,  # Run every hour
    },
    'check-attendance-warnings': {
        'task': 'courses.tasks.check_attendance_warnings',
        'schedule': 86400.0,  # Run daily
    },
} 