from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_token_created = models.DateTimeField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    email_verification_token_created = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(blank=True, null=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"

    def clean(self):
        super().clean()
        if self.failed_login_attempts >= 5 and self.account_locked_until and self.account_locked_until > timezone.now():
            raise ValidationError(_('Account is locked due to multiple failed login attempts.'))

    def lock_account(self):
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()

    def reset_login_attempts(self):
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.account_locked_until = None
        self.save()

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes after 5 failed attempts
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    semester = models.IntegerField()
    admission_date = models.DateField()
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField()
    
    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name()}"

class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    students = models.ManyToManyField(Student, through='Enrollment')
    
    def __str__(self):
        return f"{self.course_code} - {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student} - {self.course}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('student', 'course', 'date')
    
    def __str__(self):
        return f"{self.student} - {self.course} - {self.date}"

class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
        ('account_lock', 'Account Lock'),
        ('account_unlock', 'Account Unlock'),
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
        ('signup', 'Sign Up'),
        ('deactivation', 'Account Deactivation'),
        ('activation', 'Account Activation'),
        ('notice_create', 'Notice Creation'),
        ('event_attendance_mark', 'Event Attendance Marking'),
        ('enrollment_create', 'Course Enrollment'),
        ('enrollment_grade_update', 'Grade Update'),
        ('attendance_bulk_mark', 'Bulk Attendance Marking'),
    )

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities_performed',
        help_text='User who performed the action (for admin actions)'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"

class Log(models.Model):
    LEVEL_CHOICES = (
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    logger_name = models.CharField(max_length=100)
    file_path = models.CharField(max_length=255, null=True, blank=True)
    function_name = models.CharField(max_length=100, null=True, blank=True)
    line_number = models.IntegerField(null=True, blank=True)
    message = models.TextField()
    exception = models.TextField(null=True, blank=True)
    stack_trace = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='logs'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_method = models.CharField(max_length=10, null=True, blank=True)
    request_path = models.CharField(max_length=255, null=True, blank=True)
    request_body = models.TextField(null=True, blank=True)
    response_status = models.IntegerField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True)  # in milliseconds

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['level']),
            models.Index(fields=['logger_name']),
        ]

    def __str__(self):
        return f"[{self.timestamp}] {self.level}: {self.message[:100]}"