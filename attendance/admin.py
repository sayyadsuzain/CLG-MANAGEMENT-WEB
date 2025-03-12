from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Faculty, Course, AttendanceSession, AttendanceRecord

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'department')
    list_filter = ('department',)
    search_fields = ('student_id', 'user__email', 'user__first_name', 'user__last_name')

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'user', 'department')
    list_filter = ('department',)
    search_fields = ('faculty_id', 'user__email', 'user__first_name', 'user__last_name')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'name', 'faculty', 'created_at')
    list_filter = ('faculty',)
    search_fields = ('course_code', 'name', 'faculty__user__email')

class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'start_time', 'end_time', 'created_by')
    list_filter = ('course', 'date', 'created_by')
    search_fields = ('course__course_code', 'course__name')
    date_hierarchy = 'date'

class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'marked_by', 'marked_at')
    list_filter = ('status', 'session', 'marked_by')
    search_fields = ('student__user__email', 'session__course__course_code')
    date_hierarchy = 'marked_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(AttendanceSession, AttendanceSessionAdmin)
admin.site.register(AttendanceRecord, AttendanceRecordAdmin) 