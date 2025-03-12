from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/create-session/', views.create_session, name='create_session'),
    path('faculty/mark-attendance/<int:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('faculty/add-course/', views.add_course, name='add_course'),
    path('faculty/add-student/', views.add_student, name='add_student'),
    path('faculty/mark-attendance/', views.mark_attendance, name='mark_attendance_form'),
    path('faculty/manage-grades/', views.manage_grades, name='manage_grades'),
    path('faculty/course-students/<int:course_id>/', views.view_course_students, name='view_course_students'),
    path('student/view-attendance/', views.view_attendance, name='view_attendance'),
    path('student/assignments/<int:course_id>/', views.view_assignments, name='view_assignments'),
    path('student/grades/<int:course_id>/', views.view_grades, name='view_grades'),
    path('student/submit-assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('faculty/create-assignment/<int:course_id>/', views.create_assignment, name='create_assignment'),
    path('faculty/grade-assignment/<int:assignment_id>/', views.grade_assignment, name='grade_assignment'),
    path('faculty/update-grades/<int:course_id>/', views.update_grades, name='update_grades'),
    path('faculty/create-notice/', views.create_notice, name='create_notice'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty/get-course-students/<int:course_id>/', views.get_course_students, name='get_course_students'),
    path('faculty/add-student/<int:course_id>/', views.add_student_to_course, name='add_student_to_course'),
    path('faculty/remove-student/<int:course_id>/<int:student_id>/', views.remove_student_from_course, name='remove_student_from_course'),
    path('faculty/search-students/', views.search_students, name='search_students'),
    path('faculty/student-attendance-history/<int:student_id>/', views.student_attendance_history, name='student_attendance_history'),
    path('faculty/export-attendance/<int:session_id>/', views.export_attendance, name='export_attendance'),
    path('faculty/send-attendance-notifications/<int:session_id>/', views.send_attendance_notifications, name='send_attendance_notifications'),
    
    # Chat & Resource Management
    path('course/<int:course_id>/chat/', views.chat_room, name='chat_room'),
    path('course/<int:course_id>/resources/', views.course_resources, name='course_resources'),
    path('faculty/upload-resource/<int:course_id>/', views.upload_resource, name='upload_resource'),
    path('faculty/delete-resource/<int:resource_id>/', views.delete_resource, name='delete_resource'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Reports
    path('admin/generate-report/', views.generate_report, name='generate_report'),
] 