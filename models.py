from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_faculty = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'users'
        
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    
    class Meta:
        db_table = 'students'
        
    def __str__(self):
        return f"{self.user.email} - {self.roll_number}"

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'faculty'
        
    def __str__(self):
        return f"{self.user.email} - {self.designation}"

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='courses')
    students = models.ManyToManyField(Student, related_name='courses')
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        
    def __str__(self):
        return f"{self.code} - {self.name}"
        
    def get_attendance_percentage(self, student):
        total_classes = self.attendance_records.filter(date__lte=timezone.now()).count()
        if total_classes == 0:
            return 0
        attended = self.attendance_records.filter(
            student=student,
            status='PRESENT',
            date__lte=timezone.now()
        ).count()
        return round((attended / total_classes) * 100, 2)

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    marked_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'attendance_records'
        unique_together = ['course', 'student', 'date']
        indexes = [
            models.Index(fields=['course', 'student', 'date']),
            models.Index(fields=['student', 'date']),
            models.Index(fields=['course', 'date']),
        ]
        
    def __str__(self):
        return f"{self.student.roll_number} - {self.course.code} - {self.date}"
        
    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new records
            # Ensure only faculty assigned to the course can mark attendance
            if self.marked_by != self.course.faculty:
                raise ValueError("Only assigned faculty can mark attendance")
        super().save(*args, **kwargs)

class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_sessions')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance_sessions'
        unique_together = ['course', 'date']
        
    def __str__(self):
        return f"{self.course.code} - {self.date}"
        
    def mark_attendance(self, student, status, faculty, remarks=''):
        if not self.is_active:
            raise ValueError("Attendance session is closed")
            
        if faculty != self.course.faculty:
            raise ValueError("Only assigned faculty can mark attendance")
            
        attendance, created = AttendanceRecord.objects.get_or_create(
            course=self.course,
            student=student,
            date=self.date,
            defaults={
                'status': status,
                'marked_by': faculty,
                'remarks': remarks
            }
        )
        
        if not created:
            attendance.status = status
            attendance.marked_by = faculty
            attendance.remarks = remarks
            attendance.save()
            
        return attendance 