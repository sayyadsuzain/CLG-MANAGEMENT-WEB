from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Notice, Event, EventRegistration
from users.models import User, Student, Faculty

@shared_task
def send_notice_notification_async(notice_id):
    """
    Asynchronous task to send notifications for new notices.
    """
    try:
        notice = Notice.objects.select_related('created_by').get(id=notice_id)
        
        # Determine recipients based on target audience
        if notice.target_audience == 'all':
            recipients = User.objects.filter(is_active=True)
        elif notice.target_audience == 'students':
            recipients = User.objects.filter(
                is_active=True,
                student__isnull=False
            )
        elif notice.target_audience == 'faculty':
            recipients = User.objects.filter(
                is_active=True,
                faculty__isnull=False
            )
        else:
            return
        
        recipient_data = []
        for user in recipients:
            context = {
                'user_name': user.get_full_name(),
                'notice_title': notice.title,
                'notice_content': notice.content,
                'notice_type': notice.get_notice_type_display(),
                'created_by': notice.created_by.get_full_name(),
                'created_at': notice.created_at,
            }
            recipient_data.append((user.email, context))
        
        if recipient_data:
            send_bulk_email_notifications.delay(
                subject_template='New Notice: {notice_title}',
                recipient_data=recipient_data,
                template_name='new_notice'
            )
    
    except Notice.DoesNotExist:
        pass

@shared_task
def send_event_notification_async(event_id):
    """
    Asynchronous task to send notifications for new events.
    """
    try:
        event = Event.objects.select_related('organizer').get(id=event_id)
        
        # Send to all active users
        recipients = User.objects.filter(is_active=True)
        
        recipient_data = []
        for user in recipients:
            context = {
                'user_name': user.get_full_name(),
                'event_title': event.title,
                'event_description': event.description,
                'event_date': event.date,
                'event_time': event.time,
                'event_venue': event.venue,
                'organizer': event.organizer.get_full_name(),
                'registration_required': event.registration_required,
                'registration_deadline': event.registration_deadline,
            }
            recipient_data.append((user.email, context))
        
        if recipient_data:
            send_bulk_email_notifications.delay(
                subject_template='New Event: {event_title}',
                recipient_data=recipient_data,
                template_name='new_event'
            )
    
    except Event.DoesNotExist:
        pass

@shared_task
def send_event_reminder_async(event_id):
    """
    Asynchronous task to send reminders for upcoming events.
    """
    try:
        event = Event.objects.select_related('organizer').get(id=event_id)
        
        # Get registered users if registration is required, otherwise all active users
        if event.registration_required:
            recipients = User.objects.filter(
                eventregistration__event=event,
                is_active=True
            )
        else:
            recipients = User.objects.filter(is_active=True)
        
        recipient_data = []
        for user in recipients:
            context = {
                'user_name': user.get_full_name(),
                'event_title': event.title,
                'event_date': event.date,
                'event_time': event.time,
                'event_venue': event.venue,
            }
            recipient_data.append((user.email, context))
        
        if recipient_data:
            send_bulk_email_notifications.delay(
                subject_template='Reminder: {event_title} Tomorrow',
                recipient_data=recipient_data,
                template_name='event_reminder'
            )
    
    except Event.DoesNotExist:
        pass

@shared_task
def check_upcoming_events():
    """
    Periodic task to check for upcoming events and send reminders.
    """
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    upcoming_events = Event.objects.filter(date=tomorrow)
    
    for event in upcoming_events:
        send_event_reminder_async.delay(event.id)

@shared_task
def send_registration_confirmation_async(registration_id):
    """
    Asynchronous task to send event registration confirmation.
    """
    try:
        registration = EventRegistration.objects.select_related(
            'event', 'user'
        ).get(id=registration_id)
        
        context = {
            'user_name': registration.user.get_full_name(),
            'event_title': registration.event.title,
            'event_date': registration.event.date,
            'event_time': registration.event.time,
            'event_venue': registration.event.venue,
            'registration_date': registration.registration_date,
        }
        
        send_email_notification.delay(
            subject=f'Registration Confirmed: {registration.event.title}',
            recipient_email=registration.user.email,
            context=context,
            template_name='event_registration_confirmation'
        )
    
    except EventRegistration.DoesNotExist:
        pass 