from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Enrollment, Assignment, Submission, Attendance

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'course_code', 'title', 'department', 'semester',
        'faculty', 'credits', 'get_enrollment_count', 'is_active'
    )
    list_filter = ('department', 'semester', 'is_active', 'created_at')
    search_fields = ('course_code', 'title', 'faculty__user__email')
    ordering = ('semester', 'course_code')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_enrollment_count(self, obj):
        return obj.enrollments.filter(is_active=True).count()
    get_enrollment_count.short_description = 'Active Enrollments'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('faculty', 'faculty__user')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'course', 'enrollment_date',
        'grade', 'attendance_percentage', 'is_active'
    )
    list_filter = ('is_active', 'enrollment_date', 'grade')
    search_fields = (
        'student__user__email',
        'course__course_code',
        'course__title'
    )
    ordering = ('-enrollment_date',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'student__user',
            'course', 'course__faculty'
        )

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'course', 'due_date',
        'total_marks', 'get_submission_count'
    )
    list_filter = ('course__department', 'due_date', 'created_at')
    search_fields = ('title', 'course__course_code', 'course__title')
    ordering = ('-due_date',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_submission_count(self, obj):
        return obj.submissions.count()
    get_submission_count.short_description = 'Submissions'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'course__faculty')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'assignment', 'submitted_at',
        'marks_obtained', 'is_late'
    )
    list_filter = ('is_late', 'submitted_at')
    search_fields = (
        'student__user__email',
        'assignment__title',
        'assignment__course__course_code'
    )
    ordering = ('-submitted_at',)
    readonly_fields = ('is_late', 'submitted_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'student__user',
            'assignment', 'assignment__course'
        )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'course', 'date',
        'is_present', 'marked_by'
    )
    list_filter = ('is_present', 'date', 'course__department')
    search_fields = (
        'student__user__email',
        'course__course_code',
        'marked_by__user__email'
    )
    ordering = ('-date', 'course__course_code')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'student__user',
            'course', 'marked_by', 'marked_by__user'
        ) 