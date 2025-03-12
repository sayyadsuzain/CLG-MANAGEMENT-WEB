from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, EnrollmentViewSet, AssignmentViewSet,
    SubmissionViewSet, AttendanceViewSet, NotificationPreferenceViewSet,
    NotificationHistoryViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'notification-history', NotificationHistoryViewSet, basename='notification-history')

urlpatterns = [
    path('', include(router.urls)),
] 