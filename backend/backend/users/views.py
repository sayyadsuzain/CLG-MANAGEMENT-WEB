from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .models import User, Student, Faculty, Course, Enrollment, Attendance
from .serializers import (UserSerializer, StudentSerializer, FacultySerializer,
                        CourseSerializer, EnrollmentSerializer, AttendanceSerializer,
                        LoginSerializer, StudentSignupSerializer, FacultySignupSerializer,
                        PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
                        ChangePasswordSerializer, UpdateProfileSerializer)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # Get the appropriate profile data based on user type
                profile_data = None
                if user.user_type == 'student':
                    try:
                        student = Student.objects.get(user=user)
                        profile_data = StudentSerializer(student).data
                    except Student.DoesNotExist:
                        return Response(
                            {'error': 'Student profile not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                elif user.user_type == 'faculty':
                    try:
                        faculty = Faculty.objects.get(user=user)
                        profile_data = FacultySerializer(faculty).data
                    except Faculty.DoesNotExist:
                        return Response(
                            {'error': 'Faculty profile not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )

                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user.user_type,
                    'user': UserSerializer(user).data,
                    'profile': profile_data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def student_signup(self, request):
        serializer = StudentSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            student = Student.objects.get(user=user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
                'profile': StudentSerializer(student).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def faculty_signup(self, request):
        serializer = FacultySignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            faculty = Faculty.objects.get(user=user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
                'profile': FacultySerializer(faculty).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def request_password_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = get_random_string(64)
                user.password_reset_token = token
                user.password_reset_token_created = timezone.now()
                user.save()

                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
                send_mail(
                    'Password Reset Request',
                    f'Click the following link to reset your password: {reset_url}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return Response({'message': 'Password reset email sent'})
            except User.DoesNotExist:
                # For security, don't reveal if the email exists
                return Response({'message': 'Password reset email sent if email exists'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            try:
                user = User.objects.get(
                    password_reset_token=token,
                    password_reset_token_created__gte=timezone.now() - timedelta(hours=24)
                )
                user.set_password(serializer.validated_data['password'])
                user.password_reset_token = None
                user.password_reset_token_created = None
                user.save()
                return Response({'message': 'Password reset successful'})
            except User.DoesNotExist:
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        
        profile_data = None
        if user.user_type == 'student':
            student = Student.objects.get(user=user)
            profile_data = StudentSerializer(student).data
        elif user.user_type == 'faculty':
            faculty = Faculty.objects.get(user=user)
            profile_data = FacultySerializer(faculty).data

        return Response({
            'user': user_data,
            'profile': profile_data
        })

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        user = request.user
        serializer = UpdateProfileSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Invalid old password'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Existing viewsets remain unchanged... 