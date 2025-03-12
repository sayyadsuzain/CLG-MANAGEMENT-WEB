from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Count, Q
from .models import Course, Enrollment, Assignment, Submission, Attendance, NotificationPreference, NotificationHistory
from .serializers import (
    CourseSerializer, EnrollmentSerializer, AssignmentSerializer,
    SubmissionSerializer, AttendanceSerializer, NotificationPreferenceSerializer,
    NotificationHistorySerializer, NotificationHistoryListSerializer
)
from users.utils import log_user_activity
from .notifications import (
    send_new_assignment_notification, send_grade_notification,
    send_enrollment_confirmation, send_low_attendance_warning
)
from .permissions import IsEnrolledOrStaff, IsSubmissionOwnerOrStaff
from .tasks import (
    send_enrollment_confirmation_async, send_new_assignment_notification_async,
    send_grade_notification_async
)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Course.objects.all()
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by semester
        semester = self.request.query_params.get('semester')
        if semester:
            queryset = queryset.filter(semester=semester)
        
        # Filter by faculty
        faculty_id = self.request.query_params.get('faculty_id')
        if faculty_id:
            queryset = queryset.filter(faculty_id=faculty_id)
        
        # Filter active courses
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by title or course code
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(course_code__icontains=search)
            )
        
        return queryset.select_related('faculty')

    def perform_create(self, serializer):
        course = serializer.save()
        log_user_activity(
            self.request.user,
            'course_create',
            self.request,
            {'course_id': course.id, 'course_code': course.course_code}
        )

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        course = self.get_object()
        enrollments = course.enrollments.filter(is_active=True)
        return Response({
            'total_students': enrollments.count(),
            'students': EnrollmentSerializer(enrollments, many=True).data
        })

    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        course = self.get_object()
        assignments = course.assignments.all()
        return Response(AssignmentSerializer(assignments, many=True).data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        course = self.get_object()
        if not request.user.is_staff and (
            not hasattr(request.user, 'faculty') or 
            request.user.faculty != course.faculty
        ):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollments = course.enrollments.filter(is_active=True)
        attendance_data = []
        
        for enrollment in enrollments:
            total_classes = course.attendance_records.filter(
                student=enrollment.student
            ).count()
            present_classes = course.attendance_records.filter(
                student=enrollment.student,
                is_present=True
            ).count()
            
            attendance_percentage = (
                (present_classes / total_classes * 100)
                if total_classes > 0 else 0
            )
            
            attendance_data.append({
                'student': enrollment.student.user.email,
                'total_classes': total_classes,
                'present_classes': present_classes,
                'attendance_percentage': round(attendance_percentage, 2)
            })
        
        return Response(attendance_data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Enrollment.objects.all()
        
        if hasattr(user, 'student'):
            # Students can only view their own enrollments
            return queryset.filter(student=user.student)
        elif hasattr(user, 'faculty'):
            # Faculty can view enrollments in their courses
            return queryset.filter(course__faculty=user.faculty)
        elif user.is_staff:
            # Staff can view all enrollments
            return queryset
        
        return Enrollment.objects.none()

    def perform_create(self, serializer):
        enrollment = serializer.save()
        log_user_activity(
            self.request.user,
            'enrollment_create',
            self.request,
            {
                'enrollment_id': enrollment.id,
                'course_code': enrollment.course.course_code,
                'student_email': enrollment.student.user.email
            }
        )
        # Send enrollment confirmation
        send_enrollment_confirmation(enrollment)

    @action(detail=True, methods=['post'])
    def update_grade(self, request, pk=None):
        enrollment = self.get_object()
        if not request.user.is_staff and (
            not hasattr(request.user, 'faculty') or 
            request.user.faculty != enrollment.course.faculty
        ):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        grade = request.data.get('grade')
        if not grade:
            return Response(
                {'error': 'Grade is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_grade = enrollment.grade
        enrollment.grade = grade
        enrollment.save()
        
        log_user_activity(
            request.user,
            'enrollment_grade_update',
            request,
            {
                'enrollment_id': enrollment.id,
                'student_email': enrollment.student.user.email,
                'course_code': enrollment.course.course_code,
                'old_grade': old_grade,
                'new_grade': grade
            }
        )
        
        return Response(EnrollmentSerializer(enrollment).data)

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Assignment.objects.all()
        
        # Filter by course
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by due date
        due_after = self.request.query_params.get('due_after')
        if due_after:
            queryset = queryset.filter(due_date__gte=due_after)
        
        due_before = self.request.query_params.get('due_before')
        if due_before:
            queryset = queryset.filter(due_date__lte=due_before)
        
        return queryset.select_related('course', 'course__faculty')

    def perform_create(self, serializer):
        assignment = serializer.save()
        log_user_activity(
            self.request.user,
            'assignment_create',
            self.request,
            {
                'assignment_id': assignment.id,
                'course_code': assignment.course.course_code
            }
        )
        # Send notification to enrolled students
        send_new_assignment_notification(assignment)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        assignment = self.get_object()
        if not request.user.is_staff and (
            not hasattr(request.user, 'faculty') or 
            request.user.faculty != assignment.course.faculty
        ):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        submissions = assignment.submissions.all()
        return Response({
            'total_submissions': submissions.count(),
            'average_marks': submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg'],
            'submissions': SubmissionSerializer(submissions, many=True).data
        })

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Submission.objects.all()
        
        if hasattr(user, 'student'):
            # Students can only view their own submissions
            return queryset.filter(student=user.student)
        elif hasattr(user, 'faculty'):
            # Faculty can view submissions for their courses
            return queryset.filter(assignment__course__faculty=user.faculty)
        elif user.is_staff:
            # Staff can view all submissions
            return queryset
        
        return Submission.objects.none()

    @action(detail=True, methods=['post'])
    def grade_submission(self, request, pk=None):
        submission = self.get_object()
        if not request.user.is_staff and (
            not hasattr(request.user, 'faculty') or 
            request.user.faculty != submission.assignment.course.faculty
        ):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        marks = request.data.get('marks')
        remarks = request.data.get('remarks')
        
        if marks is None:
            return Response(
                {'error': 'Marks are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission.marks_obtained = marks
        submission.remarks = remarks
        submission.save()
        
        log_user_activity(
            request.user,
            'submission_grade',
            request,
            {
                'submission_id': submission.id,
                'student_email': submission.student.user.email,
                'assignment_id': submission.assignment.id,
                'marks': marks
            }
        )
        
        # Send grade notification
        send_grade_notification(submission)
        
        return Response(SubmissionSerializer(submission).data)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.all()
        
        # Filter by course
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by student
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.select_related('course', 'student', 'marked_by')

    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        course_id = request.data.get('course_id')
        date = request.data.get('date')
        attendance_data = request.data.get('attendance_data', [])
        
        if not course_id or not date or not attendance_data:
            return Response(
                {'error': 'course_id, date and attendance_data are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course = get_object_or_404(Course, id=course_id)
        if not request.user.is_staff and (
            not hasattr(request.user, 'faculty') or 
            request.user.faculty != course.faculty
        ):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        created_records = []
        for data in attendance_data:
            student_id = data.get('student_id')
            is_present = data.get('is_present', False)
            
            if not student_id:
                continue
            
            attendance, created = Attendance.objects.get_or_create(
                course=course,
                student_id=student_id,
                date=date,
                defaults={
                    'is_present': is_present,
                    'marked_by': request.user.faculty
                }
            )
            
            if not created:
                attendance.is_present = is_present
                attendance.save()
            
            created_records.append(attendance)
        
        log_user_activity(
            request.user,
            'attendance_bulk_mark',
            request,
            {
                'course_id': course.id,
                'date': date,
                'records_count': len(created_records)
            }
        )
        
        return Response(
            AttendanceSerializer(created_records, many=True).data,
            status=status.HTTP_201_CREATED
        )

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Check if preferences already exist for the user
        if NotificationPreference.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError(
                {"detail": "Notification preferences already exist for this user."}
            )
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get or create notification preferences for the current user."""
        preferences, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

class NotificationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return NotificationHistory.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationHistoryListSerializer
        return NotificationHistorySerializer

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get the count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count}) 