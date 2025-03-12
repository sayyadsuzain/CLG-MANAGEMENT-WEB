from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User, Student, Faculty
from django.utils import timezone

class Course(models.Model):
    SEMESTER_CHOICES = [
        (1, '1st Semester'),
        (2, '2nd Semester'),
        (3, '3rd Semester'),
        (4, '4th Semester'),
        (5, '5th Semester'),
        (6, '6th Semester'),
        (7, '7th Semester'),
        (8, '8th Semester'),
    ]

    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    credits = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    department = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='courses_teaching')
    syllabus = models.FileField(upload_to='course_syllabus/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['semester', 'course_code']
        unique_together = ['course_code', 'semester']

    def __str__(self):
        return f"{self.course_code} - {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    grade = models.CharField(max_length=2, null=True, blank=True)
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.student.user.email} - {self.course.course_code}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    due_date = models.DateTimeField()
    total_marks = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.course.course_code} - {self.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.user.email} - {self.assignment.title}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.is_late = self.submitted_at > self.assignment.due_date
        super().save(*args, **kwargs)

class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['course', 'student', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.user.email} - {self.course.course_code} - {self.date}"

class NotificationPreference(models.Model):
    NOTIFICATION_TYPES = [
        ('assignment', 'New Assignment'),
        ('assignment_reminder', 'Assignment Reminders'),
        ('grade', 'Grade Updates'),
        ('enrollment', 'Course Enrollment'),
        ('attendance', 'Attendance Updates'),
        ('course', 'Course Updates'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    assignment_notifications = models.BooleanField(default=True)
    assignment_reminder_notifications = models.BooleanField(default=True)
    grade_notifications = models.BooleanField(default=True)
    enrollment_notifications = models.BooleanField(default=True)
    attendance_notifications = models.BooleanField(default=True)
    course_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification Preferences for {self.user.email}"

    def is_notification_enabled(self, notification_type):
        mapping = {
            'assignment': self.assignment_notifications,
            'assignment_reminder': self.assignment_reminder_notifications,
            'grade': self.grade_notifications,
            'enrollment': self.enrollment_notifications,
            'attendance': self.attendance_notifications,
            'course': self.course_notifications,
        }
        return mapping.get(notification_type, False)

class NotificationHistory(models.Model):
    NOTIFICATION_TYPES = [
        ('assignment', 'New Assignment'),
        ('assignment_reminder', 'Assignment Reminder'),
        ('grade', 'Grade Update'),
        ('enrollment', 'Course Enrollment'),
        ('attendance', 'Attendance Update'),
        ('course', 'Course Update'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['notification_type', 'status']),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.title} ({self.status})"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])

    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_as_failed(self, error_message):
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message']) 