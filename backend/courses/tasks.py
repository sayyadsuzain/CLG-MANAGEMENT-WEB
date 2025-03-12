from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Assignment, Enrollment

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_email_notification(
    self, subject, recipient_list, template_name, context,
    from_email=None
):
    """
    Generic task for sending email notifications with HTML and plain text versions.
    Includes retry logic for handling temporary failures.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    try:
        # Render email templates
        html_content = render_to_string(
            f'courses/email/{template_name}.html',
            context
        )
        text_content = render_to_string(
            f'courses/email/{template_name}.txt',
            context
        )

        # Create email message
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            recipient_list
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Send email
        msg.send()
        
        return {
            'status': 'success',
            'recipients': recipient_list,
            'subject': subject
        }
    
    except Exception as exc:
        # Log the error and retry
        self.retry(exc=exc)

@shared_task
def send_bulk_email_notifications(
    subject_template, recipient_data, template_name,
    from_email=None
):
    """
    Task for sending bulk email notifications.
    recipient_data should be a list of tuples: (email, context)
    """
    results = []
    for email, context in recipient_data:
        # Format subject with context
        subject = subject_template.format(**context)
        
        # Schedule individual email send task
        result = send_email_notification.delay(
            subject=subject,
            recipient_list=[email],
            template_name=template_name,
            context=context,
            from_email=from_email
        )
        results.append(result.id)
    
    return {
        'status': 'scheduled',
        'task_ids': results,
        'total_recipients': len(recipient_data)
    }

@shared_task
def check_assignment_reminders():
    """
    Periodic task to check and send reminders for upcoming assignments.
    """
    # Get assignments due in the next 24 hours
    upcoming_assignments = Assignment.objects.filter(
        due_date__range=(
            timezone.now(),
            timezone.now() + timedelta(days=1)
        )
    ).select_related('course')

    for assignment in upcoming_assignments:
        # Get students who haven't submitted yet
        enrolled_students = assignment.course.enrollments.filter(
            is_active=True
        ).select_related('student__user')
        
        submitted_students = assignment.submissions.values_list(
            'student', flat=True
        )
        
        recipient_data = []
        for enrollment in enrolled_students:
            if enrollment.student.id not in submitted_students:
                student = enrollment.student.user
                context = {
                    'student_name': student.get_full_name(),
                    'assignment_title': assignment.title,
                    'course_code': assignment.course.course_code,
                    'course_title': assignment.course.title,
                    'due_date': assignment.due_date,
                }
                recipient_data.append((student.email, context))
        
        if recipient_data:
            send_bulk_email_notifications.delay(
                subject_template='Reminder: Assignment Due - {assignment_title}',
                recipient_data=recipient_data,
                template_name='assignment_reminder'
            )

@shared_task
def check_attendance_warnings():
    """
    Periodic task to check attendance percentages and send warnings.
    """
    # Get enrollments with attendance below 75%
    low_attendance_enrollments = Enrollment.objects.filter(
        is_active=True,
        attendance_percentage__lt=75
    ).select_related(
        'student__user',
        'course',
        'course__faculty__user'
    )
    
    for enrollment in low_attendance_enrollments:
        context = {
            'student_name': enrollment.student.user.get_full_name(),
            'course_code': enrollment.course.course_code,
            'course_title': enrollment.course.title,
            'attendance_percentage': enrollment.attendance_percentage,
            'faculty_name': enrollment.course.faculty.user.get_full_name(),
        }
        
        # Send to both student and faculty
        recipients = [
            enrollment.student.user.email,
            enrollment.course.faculty.user.email
        ]
        
        send_email_notification.delay(
            subject=f'Low Attendance Warning: {enrollment.course.course_code}',
            recipient_list=recipients,
            template_name='low_attendance_warning',
            context=context
        )

@shared_task
def send_new_assignment_notification_async(assignment_id):
    """
    Asynchronous task to send notifications for new assignments.
    """
    from .models import Assignment  # Import here to avoid circular imports
    
    try:
        assignment = Assignment.objects.select_related(
            'course'
        ).get(id=assignment_id)
        
        enrolled_students = assignment.course.enrollments.filter(
            is_active=True
        ).select_related('student__user')
        
        recipient_data = []
        for enrollment in enrolled_students:
            student = enrollment.student.user
            context = {
                'student_name': student.get_full_name(),
                'assignment_title': assignment.title,
                'course_code': assignment.course.course_code,
                'course_title': assignment.course.title,
                'due_date': assignment.due_date,
                'total_marks': assignment.total_marks,
            }
            recipient_data.append((student.email, context))
        
        if recipient_data:
            send_bulk_email_notifications.delay(
                subject_template='New Assignment: {assignment_title}',
                recipient_data=recipient_data,
                template_name='new_assignment'
            )
    
    except Assignment.DoesNotExist:
        # Log error or handle missing assignment
        pass

@shared_task
def send_grade_notification_async(submission_id):
    """
    Asynchronous task to send grade notifications.
    """
    from .models import Submission  # Import here to avoid circular imports
    
    try:
        submission = Submission.objects.select_related(
            'student__user',
            'assignment__course'
        ).get(id=submission_id)
        
        context = {
            'student_name': submission.student.user.get_full_name(),
            'assignment_title': submission.assignment.title,
            'course_code': submission.assignment.course.course_code,
            'course_title': submission.assignment.course.title,
            'marks_obtained': submission.marks_obtained,
            'total_marks': submission.assignment.total_marks,
            'remarks': submission.remarks,
        }
        
        send_email_notification.delay(
            subject=f'Assignment Graded: {submission.assignment.title}',
            recipient_list=[submission.student.user.email],
            template_name='grade_notification',
            context=context
        )
    
    except Submission.DoesNotExist:
        # Log error or handle missing submission
        pass

@shared_task
def send_enrollment_confirmation_async(enrollment_id):
    """
    Asynchronous task to send enrollment confirmation emails.
    """
    from .models import Enrollment  # Import here to avoid circular imports
    
    try:
        enrollment = Enrollment.objects.select_related(
            'student__user',
            'course__faculty__user'
        ).get(id=enrollment_id)
        
        context = {
            'student_name': enrollment.student.user.get_full_name(),
            'course_code': enrollment.course.course_code,
            'course_title': enrollment.course.title,
            'faculty_name': enrollment.course.faculty.user.get_full_name(),
            'semester': enrollment.course.get_semester_display(),
        }
        
        send_email_notification.delay(
            subject=f'Course Enrollment Confirmation: {enrollment.course.course_code}',
            recipient_list=[enrollment.student.user.email],
            template_name='enrollment_confirmation',
            context=context
        )
    
    except Enrollment.DoesNotExist:
        # Log error or handle missing enrollment
        pass 