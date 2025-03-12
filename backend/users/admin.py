from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Faculty, Course, Enrollment, Attendance

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_full_name', 'department', 'semester', 'admission_date')
    list_filter = ('department', 'semester')
    search_fields = ('student_id', 'user__username', 'user__email', 'department')
    ordering = ('-admission_date',)

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'get_full_name', 'department', 'designation', 'joining_date')
    list_filter = ('department', 'designation')
    search_fields = ('faculty_id', 'user__username', 'user__email', 'department')
    ordering = ('-joining_date',)

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'get_faculty_name', 'created_at')
    list_filter = ('faculty__department',)
    search_fields = ('course_code', 'title', 'faculty__user__username')
    ordering = ('course_code',)

    def get_faculty_name(self, obj):
        if obj.faculty:
            return f"{obj.faculty.user.first_name} {obj.faculty.user.last_name}"
        return "No Faculty Assigned"
    get_faculty_name.short_description = 'Faculty'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('get_student_id', 'get_course_code', 'enrollment_date', 'grade')
    list_filter = ('enrollment_date', 'grade')
    search_fields = ('student__student_id', 'course__course_code')
    ordering = ('-enrollment_date',)

    def get_student_id(self, obj):
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'

    def get_course_code(self, obj):
        return obj.course.course_code
    get_course_code.short_description = 'Course Code'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_student_id', 'get_course_code', 'date', 'is_present')
    list_filter = ('date', 'is_present')
    search_fields = ('student__student_id', 'course__course_code')
    ordering = ('-date',)

    def get_student_id(self, obj):
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'

    def get_course_code(self, obj):
        return obj.course.course_code
    get_course_code.short_description = 'Course Code'

admin.site.register(User, CustomUserAdmin) 