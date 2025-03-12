from rest_framework import serializers
from django.utils import timezone
from .models import (
    Course, Enrollment, Assignment, Submission, Attendance,
    NotificationPreference, NotificationHistory
)
from users.serializers import UserSerializer, StudentSerializer, FacultySerializer

class CourseSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.PrimaryKeyRelatedField(
        source='faculty',
        queryset=Faculty.objects.all(),
        write_only=True,
        required=False
    )
    enrollment_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id', 'course_code', 'title', 'description', 'credits',
            'semester', 'department', 'faculty', 'faculty_id',
            'syllabus', 'is_active', 'created_at', 'updated_at',
            'enrollment_count', 'is_enrolled'
        )

    def get_enrollment_count(self, obj):
        return obj.enrollments.filter(is_active=True).count()

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student'):
            return obj.enrollments.filter(
                student=request.user.student,
                is_active=True
            ).exists()
        return False

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        source='course',
        queryset=Course.objects.all(),
        write_only=True
    )

    class Meta:
        model = Enrollment
        fields = (
            'id', 'student', 'course', 'course_id', 'enrollment_date',
            'is_active', 'grade', 'attendance_percentage'
        )
        read_only_fields = ('enrollment_date', 'grade', 'attendance_percentage')

    def validate_course_id(self, course):
        user = self.context['request'].user
        if not hasattr(user, 'student'):
            raise serializers.ValidationError("Only students can enroll in courses.")
        
        if Enrollment.objects.filter(
            student=user.student,
            course=course,
            is_active=True
        ).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")
        
        return course

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user.student
        return super().create(validated_data)

class AssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        source='course',
        queryset=Course.objects.all(),
        write_only=True
    )
    submission_count = serializers.SerializerMethodField()
    has_submitted = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            'id', 'course', 'course_id', 'title', 'description',
            'file', 'due_date', 'total_marks', 'created_at',
            'updated_at', 'submission_count', 'has_submitted'
        )

    def get_submission_count(self, obj):
        return obj.submissions.count()

    def get_has_submitted(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student'):
            return obj.submissions.filter(student=request.user.student).exists()
        return False

    def validate_course_id(self, course):
        user = self.context['request'].user
        if not user.is_staff and (
            not hasattr(user, 'faculty') or 
            user.faculty != course.faculty
        ):
            raise serializers.ValidationError(
                "Only course faculty can create assignments."
            )
        return course

class SubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    assignment_id = serializers.PrimaryKeyRelatedField(
        source='assignment',
        queryset=Assignment.objects.all(),
        write_only=True
    )
    student = StudentSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = (
            'id', 'assignment', 'assignment_id', 'student', 'file',
            'submitted_at', 'marks_obtained', 'remarks', 'is_late'
        )
        read_only_fields = ('submitted_at', 'marks_obtained', 'remarks', 'is_late')

    def validate_assignment_id(self, assignment):
        user = self.context['request'].user
        if not hasattr(user, 'student'):
            raise serializers.ValidationError("Only students can submit assignments.")
        
        if Submission.objects.filter(
            assignment=assignment,
            student=user.student
        ).exists():
            raise serializers.ValidationError(
                "You have already submitted this assignment."
            )
        
        if assignment.due_date < timezone.now():
            # Allow submission but mark as late
            self.context['is_late'] = True
        
        return assignment

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user.student
        validated_data['is_late'] = self.context.get('is_late', False)
        return super().create(validated_data)

class AttendanceSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        source='course',
        queryset=Course.objects.all(),
        write_only=True
    )
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=Student.objects.all(),
        write_only=True
    )
    marked_by = FacultySerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = (
            'id', 'course', 'course_id', 'student', 'student_id',
            'date', 'is_present', 'marked_by', 'created_at'
        )
        read_only_fields = ('created_at',)

    def validate(self, data):
        user = self.context['request'].user
        course = data['course']
        
        if not user.is_staff and (
            not hasattr(user, 'faculty') or 
            user.faculty != course.faculty
        ):
            raise serializers.ValidationError(
                "Only course faculty can mark attendance."
            )
        
        # Check if attendance already marked for this date
        if Attendance.objects.filter(
            course=course,
            student=data['student'],
            date=data['date']
        ).exists():
            raise serializers.ValidationError(
                "Attendance already marked for this date."
            )
        
        return data

    def create(self, validated_data):
        validated_data['marked_by'] = self.context['request'].user.faculty
        return super().create(validated_data)

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            'id', 'user', 'assignment_notifications',
            'assignment_reminder_notifications', 'grade_notifications',
            'enrollment_notifications', 'attendance_notifications',
            'course_notifications', 'email_notifications',
            'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'created_at', 'updated_at')

    def create(self, validated_data):
        user = self.context['request'].user
        return NotificationPreference.objects.create(user=user, **validated_data)

class NotificationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationHistory
        fields = (
            'id', 'user', 'notification_type', 'title',
            'message', 'status', 'error_message', 'is_read',
            'created_at', 'sent_at', 'related_object_type',
            'related_object_id'
        )
        read_only_fields = (
            'user', 'status', 'error_message', 'created_at',
            'sent_at'
        )

class NotificationHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationHistory
        fields = (
            'id', 'notification_type', 'title',
            'status', 'is_read', 'created_at', 'sent_at'
        ) 