from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import Course, Student, Faculty, AttendanceRecord, AttendanceSession
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, date

class IsFacultyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_faculty

class CourseAttendanceView(LoginRequiredMixin, IsFacultyMixin, DetailView):
    model = Course
    template_name = 'attendance/course_attendance.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Ensure faculty is assigned to this course
        if course.faculty.user != self.request.user:
            raise PermissionDenied("You are not authorized to view this course's attendance")
        
        context['students'] = course.students.all()
        context['today'] = date.today()
        
        # Get or create today's attendance session
        session, created = AttendanceSession.objects.get_or_create(
            course=course,
            date=context['today'],
            defaults={
                'start_time': timezone.now().time(),
                'end_time': timezone.now().replace(hour=23, minute=59, second=59).time(),
                'created_by': course.faculty
            }
        )
        context['session'] = session
        
        # Get existing attendance records for today
        context['attendance_records'] = {
            record.student_id: record.status
            for record in AttendanceRecord.objects.filter(
                course=course,
                date=context['today']
            )
        }
        
        return context

@login_required
def mark_attendance(request, course_id):
    if not request.user.is_faculty:
        return JsonResponse({'error': 'Only faculty can mark attendance'}, status=403)
    
    course = get_object_or_404(Course, id=course_id)
    faculty = request.user.faculty_profile
    
    # Verify faculty is assigned to this course
    if course.faculty != faculty:
        return JsonResponse({'error': 'You are not authorized to mark attendance for this course'}, status=403)
    
    try:
        data = request.POST
        student_id = data.get('student_id')
        status = data.get('status')
        remarks = data.get('remarks', '')
        
        student = get_object_or_404(Student, id=student_id)
        
        # Get or create today's session
        session = AttendanceSession.objects.get_or_create(
            course=course,
            date=date.today(),
            defaults={
                'start_time': timezone.now().time(),
                'end_time': timezone.now().replace(hour=23, minute=59, second=59).time(),
                'created_by': faculty
            }
        )[0]
        
        # Mark attendance using session
        with transaction.atomic():
            attendance = session.mark_attendance(student, status, faculty, remarks)
        
        return JsonResponse({
            'success': True,
            'message': f'Attendance marked for {student.user.get_full_name()}',
            'attendance': {
                'status': attendance.status,
                'marked_at': attendance.marked_at.isoformat(),
                'marked_by': attendance.marked_by.user.get_full_name()
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

class StudentAttendanceView(LoginRequiredMixin, ListView):
    template_name = 'attendance/student_attendance.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        if not self.request.user.is_student:
            raise PermissionDenied("Only students can view their attendance")
        
        student = self.request.user.student_profile
        return Course.objects.filter(students=student, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Calculate attendance percentages for each course
        context['attendance_data'] = {}
        for course in context['courses']:
            attendance_records = AttendanceRecord.objects.filter(
                course=course,
                student=student
            )
            total_classes = attendance_records.count()
            attended_classes = attendance_records.filter(status='PRESENT').count()
            
            context['attendance_data'][course.id] = {
                'total_classes': total_classes,
                'attended_classes': attended_classes,
                'percentage': course.get_attendance_percentage(student),
                'recent_records': attendance_records.order_by('-date')[:5]
            }
        
        return context

class AttendanceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_faculty:
            return AttendanceRecord.objects.filter(
                course__faculty=self.request.user.faculty_profile
            )
        elif self.request.user.is_student:
            return AttendanceRecord.objects.filter(
                student=self.request.user.student_profile
            )
        return AttendanceRecord.objects.none()
    
    @action(detail=False, methods=['get'])
    def course_summary(self, request, course_pk=None):
        course = get_object_or_404(Course, pk=course_pk)
        
        if request.user.is_faculty and course.faculty != request.user.faculty_profile:
            return Response({'error': 'Not authorized'}, status=403)
            
        if request.user.is_student and not course.students.filter(id=request.user.student_profile.id).exists():
            return Response({'error': 'Not authorized'}, status=403)
        
        summary = {
            'course_code': course.code,
            'course_name': course.name,
            'total_classes': AttendanceRecord.objects.filter(course=course).count(),
            'attendance_by_date': {}
        }
        
        records = AttendanceRecord.objects.filter(course=course).order_by('date')
        for record in records:
            date_str = record.date.isoformat()
            if date_str not in summary['attendance_by_date']:
                summary['attendance_by_date'][date_str] = {
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                    'total': 0
                }
            
            summary['attendance_by_date'][date_str][record.status.lower()] += 1
            summary['attendance_by_date'][date_str]['total'] += 1
        
        return Response(summary) 