from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from attendance import views

router = DefaultRouter()
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='attendance/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Faculty URLs
    path('faculty/course/<int:pk>/attendance/', views.CourseAttendanceView.as_view(), name='course_attendance'),
    path('faculty/mark-attendance/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    
    # Student URLs
    path('student/attendance/', views.StudentAttendanceView.as_view(), name='student_attendance'),
    
    # API endpoints
    path('api/course/<int:course_pk>/summary/', views.AttendanceViewSet.as_view({'get': 'course_summary'}), name='course_summary'),
] 