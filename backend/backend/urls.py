from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from users.views import (UserViewSet, StudentViewSet, FacultyViewSet,
                        CourseViewSet, EnrollmentViewSet, AttendanceViewSet,
                        AuthViewSet, UserProfileViewSet)
from notices.views import NoticeViewSet, EventViewSet, EventRegistrationViewSet

# Swagger documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="College Management System API",
        default_version='v1',
        description="API documentation for College Management System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@cms.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'faculty', FacultyViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'notices', NoticeViewSet)
router.register(r'events', EventViewSet)
router.register(r'event-registrations', EventRegistrationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Swagger documentation URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 