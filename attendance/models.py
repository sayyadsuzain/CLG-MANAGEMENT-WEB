from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
# import qrcode
# from io import BytesIO
# from django.core.files import File
# from PIL import Image
import uuid
import os

def validate_image_file(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Please use: jpg, jpeg, png, or gif')
    if value.size > 5*1024*1024:  # 5MB limit
        raise ValidationError('File size too large. Size should not exceed 5MB.')

class User(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.FileField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        validators=[validate_image_file]
    )
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def get_user_type_display(self):
        return dict(self.USER_TYPES).get(self.user_type, '')

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    semester = models.IntegerField(default=1)
    qr_code = models.FileField(upload_to='qr_codes/', blank=True, null=True)
    roll_number = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

    def get_attendance_percentage(self):
        total_sessions = AttendanceSession.objects.filter(course__in=self.courses.all()).count()
        if total_sessions == 0:
            return 0
        present_sessions = AttendanceRecord.objects.filter(
            student=self,
            status=True
        ).count()
        return (present_sessions / total_sessions) * 100

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, default='Assistant Professor')
    joining_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.faculty_id})"

class AttendancePolicy(models.Model):
    """Model to define attendance policies"""
    name = models.CharField(max_length=100)
    min_attendance_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=75.00
    )
    warning_threshold = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=80.00,
        help_text="Threshold at which warnings are sent"
    )
    auto_notify_student = models.BooleanField(default=True)
    auto_notify_faculty = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} (Min: {self.min_attendance_percentage}%)"

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    students = models.ManyToManyField('Student', related_name='courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_code} - {self.name}"
    
    def get_attendance_stats(self):
        """Get attendance statistics for this course"""
        total_students = self.students.count()
        total_sessions = AttendanceSession.objects.filter(course=self).count()
        
        if total_students == 0 or total_sessions == 0:
            return {
                'average_attendance': 0,
                'below_threshold_count': 0,
                'total_students': total_students,
                'total_sessions': total_sessions
            }
        
        # Calculate average attendance
        attendance_sum = 0
        below_threshold_count = 0
        threshold = 75  # Default threshold
        
        if self.attendance_policy:
            threshold = self.attendance_policy.min_attendance_percentage
        
        for student in self.students.all():
            percentage = student.get_attendance_percentage()
            attendance_sum += percentage
            
            if percentage < threshold:
                below_threshold_count += 1
        
        return {
            'average_attendance': attendance_sum / total_students,
            'below_threshold_count': below_threshold_count,
            'total_students': total_students,
            'total_sessions': total_sessions
        }

class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_by = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    session_type = models.CharField(
        max_length=20, 
        choices=[
            ('regular', 'Regular Class'),
            ('lab', 'Laboratory'),
            ('tutorial', 'Tutorial'),
            ('extra', 'Extra Class'),
            ('makeup', 'Makeup Class')
        ],
        default='regular'
    )
    qr_code = models.FileField(upload_to='session_qrcodes/', blank=True, null=True)
    session_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['course', 'date', 'start_time']

    def __str__(self):
        return f"{self.course.course_code} - {self.date} ({self.start_time} to {self.end_time})"
    
    def save(self, *args, **kwargs):
        # QR code generation disabled temporarily
        # if not self.qr_code:
        #     qr = qrcode.QRCode(
        #         version=1,
        #         error_correction=qrcode.constants.ERROR_CORRECT_L,
        #         box_size=10,
        #         border=4,
        #     )
        #     qr.add_data(str(self.session_uuid))
        #     qr.make(fit=True)
        #     
        #     img = qr.make_image(fill_color="black", back_color="white")
        #     buffer = BytesIO()
        #     img.save(buffer, format="PNG")
        #     
        #     filename = f'session_qr_{self.session_uuid}.png'
        #     self.qr_code.save(filename, File(buffer), save=False)
        
        super().save(*args, **kwargs)
    
    def get_attendance_count(self):
        """Get count of present and absent students"""
        total_students = self.course.students.count()
        present_count = AttendanceRecord.objects.filter(
            session=self,
            status=True
        ).count()
        
        return {
            'total': total_students,
            'present': present_count,
            'absent': total_students - present_count,
            'percentage': (present_count / total_students * 100) if total_students > 0 else 0
        }
    
    def close_session(self):
        """Close the session and mark absent for students who haven't been marked"""
        if self.is_active:
            # Get all students who haven't been marked
            marked_students = AttendanceRecord.objects.filter(
                session=self
            ).values_list('student_id', flat=True)
            
            unmarked_students = self.course.students.exclude(id__in=marked_students)
            
            # Mark them as absent
            for student in unmarked_students:
                AttendanceRecord.objects.create(
                    session=self,
                    student=student,
                    status=False,
                    marked_by=self.created_by,
                    marked_at=timezone.now()
                )
            
            self.is_active = False
            self.save()

class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)  # True for present, False for absent
    marked_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Get the course from the session
        course = self.session.course
        
        # Save the record first
        super().save(*args, **kwargs)
        
        # Send notification if student is absent
        if not self.status:  # If student is absent
            try:
                # Create notification for student
                Notification.objects.create(
                    user=self.student.user,
                    title=f'Absence Notification - {course.name}',
                    message=f'You were marked absent for {course.name} on {self.session.date}',
                    notification_type='attendance'
                )
            except Exception as e:
                # Log the error but don't prevent saving
                print(f"Error creating notification: {str(e)}")
    
    class Meta:
        unique_together = ('session', 'student')
        
    def __str__(self):
        return f"{self.student} - {self.session} - {'Present' if self.status else 'Absent'}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField()
    created_by = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.course_code} - {self.title}"
    
    @property
    def is_past_due(self):
        return timezone.now().date() > self.due_date.date()

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.assignment.title}"
    
    @property
    def is_late(self):
        return self.submitted_at.date() > self.assignment.due_date.date()

class Grade(models.Model):
    GRADE_CHOICES = (
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.course_code} - {self.grade}"

class Notice(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_recent(self):
        return (timezone.now() - self.created_at).days <= 7

def validate_pdf_file(value):
    if not value:
        return
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.pdf':
        raise ValidationError('Only PDF files are allowed.')

class Resource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='resources/',
        validators=[validate_pdf_file, FileExtensionValidator(['pdf'])],
        help_text="Only PDF files are allowed"
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.course_code}"
    
    class Meta:
        ordering = ['-uploaded_at']
    
    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else None
    
    def get_download_url(self):
        if self.file:
            try:
                return self.file.url
            except Exception:
                return None
        return None
    
    def clean(self):
        if self.file:
            if not self.file.name.lower().endswith('.pdf'):
                raise ValidationError('Only PDF files are allowed.')
            # Only check if file exists if it's already been saved
            if self.pk and not os.path.exists(self.file.path):
                raise ValidationError('File does not exist.')
        super().clean()
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        # Delete the file when the model instance is deleted
        if self.file:
            try:
                storage = self.file.storage
                if storage.exists(self.file.name):
                    storage.delete(self.file.name)
            except Exception:
                pass
        super().delete(*args, **kwargs)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('attendance', 'Attendance'),
        ('grade', 'Grade'),
        ('assignment', 'Assignment'),
        ('resource', 'Resource'),
        ('notice', 'Notice'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    related_id = models.IntegerField(null=True, blank=True)  # ID of related object (assignment, resource, etc.)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']

class AttendanceReport(models.Model):
    """Model to store generated attendance reports"""
    REPORT_TYPES = [
        ('student', 'Individual Student'),
        ('course', 'Course Report'),
        ('department', 'Department Report'),
        ('custom', 'Custom Report')
    ]
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    report_file = models.FileField(upload_to='attendance_reports/', null=True, blank=True)
    report_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.report_type} ({self.start_date} to {self.end_date})"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']