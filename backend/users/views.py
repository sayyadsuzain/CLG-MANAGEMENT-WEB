from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import timedelta
from .models import User, Student, Faculty, Course, Enrollment, Attendance, UserActivity, Log
from .serializers import (
    UserSerializer, StudentSerializer, FacultySerializer,
    CourseSerializer, EnrollmentSerializer, AttendanceSerializer,
    LoginSerializer, StudentSignupSerializer, FacultySignupSerializer,
    EmailVerificationSerializer, UserDetailSerializer, UserUpdateSerializer,
    AdminUserUpdateSerializer, UserActivitySerializer, LogSerializer
)
from django.db import models
from .utils import log_user_activity, get_redirect_url_by_role
from django_filters import rest_framework as filters
import logging

logger = logging.getLogger(__name__)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def send_verification_email(self, user, request):
        token = get_random_string(64)
        user.email_verification_token = token
        user.email_verification_token_created = timezone.now()
        user.save()

        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        context = {
            'user': user,
            'verification_url': verification_url
        }
        
        html_message = render_to_string('email/verify_email.html', context)
        plain_message = render_to_string('email/verify_email.txt', context)

        send_mail(
            'Verify your email address',
            plain_message,
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @action(detail=False, methods=['post'])
    def login(self, request):
        try:
            print(f"Login attempt with data: {request.data}")
            
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                print(f"Serializer errors: {serializer.errors}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            print(f"Attempting to authenticate user: {email}")
            user = authenticate(request, email=email, password=password)
            print(f"Authentication result: {user}")
            
            if user is None:
                print("Authentication failed - invalid credentials")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if not user.is_active:
                print(f"User {email} is inactive")
                return Response(
                    {'error': 'Account is inactive'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if not user.email_verified:
                print(f"User {email} email not verified")
                return Response(
                    {'error': 'Email not verified'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate tokens
            print("Generating tokens")
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            # Get user role and redirect URL
            redirect_data = get_redirect_url_by_role(user)
            print(f"Redirect data: {redirect_data}")
            
            # Log login activity
            try:
                activity = log_user_activity(
                    user=user,
                    activity_type='login',
                    request=request,
                    extra_data={'login_successful': True}
                )
                print(f"Login activity logged: {activity}")
            except Exception as e:
                print(f"Error logging activity: {str(e)}")
                logger.error(f"Failed to log login activity: {str(e)}")
            
            # Update last login
            user.last_login = timezone.now()
            user.save()
            
            response_data = {
                'tokens': tokens,
                'user': UserDetailSerializer(user).data,
                'redirect': redirect_data
            }
            print(f"Login successful for user: {email}")
            return Response(response_data)
            
        except Exception as e:
            print(f"Unexpected error during login: {str(e)}")
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def student_signup(self, request):
        serializer = StudentSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate verification token
            token = get_random_string(64)
            user.email_verification_token = token
            user.email_verification_sent_at = timezone.now()
            user.save()
            
            # Send verification email
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            context = {
                'user_name': user.get_full_name(),
                'verification_url': verification_url
            }
            
            send_mail(
                subject='Verify your email address',
                message=render_to_string('email/email_verification.txt', context),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=render_to_string('email/email_verification.html', context)
            )
            
            log_user_activity(
                user=user,
                activity_type='signup',
                request=request,
                extra_data={'user_type': 'student'}
            )
            
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def faculty_signup(self, request):
        serializer = FacultySignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate verification token
            token = get_random_string(64)
            user.email_verification_token = token
            user.email_verification_sent_at = timezone.now()
            user.save()
            
            # Send verification email
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            context = {
                'user_name': user.get_full_name(),
                'verification_url': verification_url
            }
            
            send_mail(
                subject='Verify your email address',
                message=render_to_string('email/email_verification.txt', context),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=render_to_string('email/email_verification.html', context)
            )
            
            log_user_activity(
                user=user,
                activity_type='signup',
                request=request,
                extra_data={'user_type': 'faculty'}
            )
            
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            try:
                user = User.objects.get(
                    email_verification_token=token,
                    email_verified=False
                )
                
                # Check if token is expired (24 hours)
                if user.email_verification_sent_at < timezone.now() - timedelta(hours=24):
                    return Response(
                        {'error': 'Verification link has expired'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user.email_verified = True
                user.email_verification_token = None
                user.email_verification_sent_at = None
                user.save()
                
                log_user_activity(
                    user=user,
                    activity_type='email_verification',
                    request=request,
                    extra_data={'verified': True}
                )
                
                # Get redirect URL based on user role
                redirect_data = get_redirect_url_by_role(user)
                
                return Response({
                    'message': 'Email verification successful',
                    'redirect': redirect_data
                })
                
            except User.DoesNotExist:
                return Response(
                    {'error': 'Invalid verification token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        if request.user.is_authenticated:
            log_user_activity(
                user=request.user,
                activity_type='logout',
                request=request
            )
        return Response({'message': 'Logged out successfully'})

    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email, email_verified=False)
            
            # Generate new verification token
            token = get_random_string(64)
            user.email_verification_token = token
            user.email_verification_sent_at = timezone.now()
            user.save()
            
            # Send verification email
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            context = {
                'user_name': user.get_full_name(),
                'verification_url': verification_url
            }
            
            send_mail(
                subject='Verify your email address',
                message=render_to_string('email/email_verification.txt', context),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=render_to_string('email/email_verification.html', context)
            )
            
            log_user_activity(
                user=user,
                activity_type='resend_verification',
                request=request
            )
            
            return Response({
                'message': 'Verification email sent successfully'
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'No unverified user found with this email'},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Regular users can only view their own profile
        if not self.request.user.is_staff:
            return queryset.filter(id=self.request.user.id)
        
        # Staff can filter users
        user_type = self.request.query_params.get('user_type', None)
        is_active = self.request.query_params.get('is_active', None)
        department = self.request.query_params.get('department', None)
        search = self.request.query_params.get('search', None)

        if user_type:
            queryset = queryset.filter(user_type=user_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if department:
            queryset = queryset.filter(
                models.Q(student__department=department) |
                models.Q(faculty__department=department)
            )
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(username__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            if self.request.user.is_staff:
                return AdminUserUpdateSerializer
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # Check if password is being changed
            if 'new_password' in serializer.validated_data:
                log_user_activity(user, 'password_change', request)
            else:
                log_user_activity(user, 'profile_update', request)
            
            serializer.save()
            return Response(UserDetailSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.is_active = True
        user.save()
        
        # Log activation activity
        log_user_activity(user, 'activation', request, performed_by=request.user)
        
        return Response({'message': f'User {user.email} activated successfully'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        
        # Prevent deactivating the last superuser
        if user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
            return Response(
                {'error': 'Cannot deactivate the last superuser'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent self-deactivation
        if user == request.user:
            return Response(
                {'error': 'Cannot deactivate your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save()
        
        # Log deactivation activity
        log_user_activity(user, 'deactivation', request, performed_by=request.user)
        
        return Response({'message': f'User {user.email} deactivated successfully'})

    @action(detail=True, methods=['post'])
    def unlock_account(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.save()
        
        # Log account unlock activity
        log_user_activity(user, 'account_unlock', request, performed_by=request.user)
        
        return Response({'message': f'Account unlocked for {user.email}'})

    @action(detail=True, methods=['post'])
    def force_password_reset(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        token = get_random_string(64)
        user.password_reset_token = token
        user.password_reset_token_created = timezone.now()
        user.save()

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        # Send password reset email
        send_mail(
            'Password Reset Required',
            f'Your password has been reset by an administrator. Please set a new password using this link: {reset_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return Response({'message': f'Password reset initiated for {user.email}'})

    @action(detail=False, methods=['get'])
    def my_activities(self, request):
        """Get activities for the current user."""
        activities = UserActivity.objects.filter(user=request.user)
        
        # Filter by activity type if specified
        activity_type = request.query_params.get('activity_type')
        if activity_type:
            activities = activities.filter(activity_type=activity_type)
        
        # Filter by date range if specified
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            activities = activities.filter(created_at__gte=start_date)
        if end_date:
            activities = activities.filter(created_at__lte=end_date)
        
        # Paginate results
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = UserActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get activities for a specific user (admin only)."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        activities = UserActivity.objects.filter(user=user)
        
        # Filter by activity type if specified
        activity_type = request.query_params.get('activity_type')
        if activity_type:
            activities = activities.filter(activity_type=activity_type)
        
        # Filter by date range if specified
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            activities = activities.filter(created_at__gte=start_date)
        if end_date:
            activities = activities.filter(created_at__lte=end_date)
        
        # Paginate results
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = UserActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def all_activities(self, request):
        """Get all user activities (admin only)."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        activities = UserActivity.objects.all()
        
        # Filter by user if specified
        user_id = request.query_params.get('user_id')
        if user_id:
            activities = activities.filter(user_id=user_id)
        
        # Filter by activity type if specified
        activity_type = request.query_params.get('activity_type')
        if activity_type:
            activities = activities.filter(activity_type=activity_type)
        
        # Filter by date range if specified
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            activities = activities.filter(created_at__gte=start_date)
        if end_date:
            activities = activities.filter(created_at__lte=end_date)
        
        # Paginate results
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = UserActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        student = self.get_object()
        enrollments = Enrollment.objects.filter(student=student)
        courses = [enrollment.course for enrollment in enrollments]
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        student = self.get_object()
        attendance = Attendance.objects.filter(student=student)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        faculty = self.get_object()
        courses = Course.objects.filter(faculty=faculty)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def enroll_student(self, request, pk=None):
        course = self.get_object()
        student_id = request.data.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            course=course
        )
        
        if created:
            return Response({'message': 'Student enrolled successfully'})
        return Response({'message': 'Student already enrolled'})

    @action(detail=True, methods=['post'])
    def mark_attendance(self, request, pk=None):
        course = self.get_object()
        student_id = request.data.get('student_id')
        date = request.data.get('date')
        is_present = request.data.get('is_present', False)
        
        student = get_object_or_404(Student, id=student_id)
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            course=course,
            date=date,
            defaults={'is_present': is_present}
        )
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Enrollment.objects.all()
        student_id = self.request.query_params.get('student_id', None)
        course_id = self.request.query_params.get('course_id', None)
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Attendance.objects.all()
        student_id = self.request.query_params.get('student_id', None)
        course_id = self.request.query_params.get('course_id', None)
        date = self.request.query_params.get('date', None)
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if date:
            queryset = queryset.filter(date=date)
        
        return queryset

class LogFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    level = filters.ChoiceFilter(choices=Log.LEVEL_CHOICES)
    logger_name = filters.CharFilter(lookup_expr='icontains')
    user_email = filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    message = filters.CharFilter(lookup_expr='icontains')
    ip_address = filters.CharFilter(lookup_expr='icontains')
    request_path = filters.CharFilter(lookup_expr='icontains')
    response_status = filters.NumberFilter()
    min_execution_time = filters.NumberFilter(field_name='execution_time', lookup_expr='gte')
    max_execution_time = filters.NumberFilter(field_name='execution_time', lookup_expr='lte')

    class Meta:
        model = Log
        fields = ['level', 'logger_name', 'user_email', 'message', 'ip_address',
                 'request_path', 'response_status', 'min_execution_time',
                 'max_execution_time']

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing logs.
    """
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = LogFilter
    ordering_fields = ['timestamp', 'level', 'logger_name', 'execution_time']
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Additional filtering options
        has_error = self.request.query_params.get('has_error', None)
        if has_error is not None:
            has_error = has_error.lower() == 'true'
            if has_error:
                queryset = queryset.exclude(exception__isnull=True)
            else:
                queryset = queryset.filter(exception__isnull=True)

        # Performance filtering
        slow_requests = self.request.query_params.get('slow_requests', None)
        if slow_requests is not None:
            threshold = float(slow_requests)  # milliseconds
            queryset = queryset.filter(execution_time__gte=threshold)

        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get a summary of logs including counts by level, average execution time, etc.
        """
        total_logs = Log.objects.count()
        level_counts = Log.objects.values('level').annotate(count=models.Count('id'))
        avg_execution_time = Log.objects.filter(execution_time__isnull=False).aggregate(
            avg_time=models.Avg('execution_time')
        )['avg_time']
        error_count = Log.objects.filter(level__in=['ERROR', 'CRITICAL']).count()
        
        return Response({
            'total_logs': total_logs,
            'level_counts': level_counts,
            'avg_execution_time': avg_execution_time,
            'error_count': error_count,
        })

    @action(detail=False, methods=['get'])
    def error_summary(self, request):
        """
        Get a summary of errors grouped by exception type.
        """
        error_logs = Log.objects.filter(
            level__in=['ERROR', 'CRITICAL'],
            exception__isnull=False
        )
        error_types = error_logs.values('exception').annotate(
            count=models.Count('id'),
            last_occurred=models.Max('timestamp')
        ).order_by('-count')
        
        return Response(error_types) 