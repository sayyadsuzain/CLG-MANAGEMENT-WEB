from django.db import models
from users.models import User
import logging

logger = logging.getLogger(__name__)

class Notice(models.Model):
    NOTICE_TYPES = (
        ('announcement', 'Announcement'),
        ('event', 'Event'),
        ('academic', 'Academic'),
        ('exam', 'Examination'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    notice_type = models.CharField(max_length=20, choices=NOTICE_TYPES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to='notice_attachments/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    target_audience = models.CharField(max_length=50, choices=(
        ('all', 'All'),
        ('students', 'Students'),
        ('faculty', 'Faculty'),
    ))
    
    def __str__(self):
        return f"{self.title} - {self.notice_type}"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.date}"

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    attendance_status = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('event', 'user')
    
    def __str__(self):
        return f"{self.user} - {self.event}"

# Log different levels
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message', exc_info=True)  # Include stack trace 