from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime
from .models import User, Student, Faculty, Course, AttendanceSession, AttendanceRecord, Assignment, Grade, Notice, AssignmentSubmission, Resource, Notification
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.mail import send_mail
import csv
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Verify user type matches
            if user_type == 'student' and user.user_type != 'student':
                messages.error(request, 'Invalid student credentials')
                return render(request, 'login.html')
            elif user_type == 'faculty' and user.user_type != 'faculty':
                messages.error(request, 'Invalid faculty credentials')
                return render(request, 'login.html')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            
            if user.is_superuser:
                return redirect('attendance:admin_dashboard')
            elif user.user_type == 'student':
                return redirect('attendance:student_dashboard')
            else:
                return redirect('attendance:faculty_dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type')
        department = request.POST.get('department')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'register.html')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )
        
        if user_type == 'student':
            Student.objects.create(
                user=user,
                student_id=f"STU{user.id:04d}",
                department=department
            )
        else:
            Faculty.objects.create(
                user=user,
                faculty_id=f"FAC{user.id:04d}",
                department=department
            )
        
        messages.success(request, 'Registration successful. Please login.')
        return redirect('attendance:login')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('attendance:login')

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    student = request.user.student
    courses = Course.objects.filter(students=student)
    
    # Get attendance data
    attendance_data = []
    total_attendance_percentage = 0
    total_pending_assignments = 0
    grades = []
    
    for course in courses:
        total_sessions = AttendanceSession.objects.filter(course=course).count()
        attended_sessions = AttendanceRecord.objects.filter(
            session__course=course,
            student=student,
            status=True
        ).count()
        
        attendance_percentage = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
        total_attendance_percentage += attendance_percentage
        
        # Get pending assignments
        pending_assignments = Assignment.objects.filter(
            course=course,
            due_date__gte=timezone.now().date()
        ).exclude(submissions__student=student)
        
        total_pending_assignments += pending_assignments.count()
        
        # Get latest grade
        latest_grade = Grade.objects.filter(
            student=student,
            course=course
        ).order_by('-updated_at').first()
        
        if latest_grade:
            grades.append(latest_grade.grade)
        
        attendance_data.append({
            'course': course,
            'total_sessions': total_sessions,
            'attended_sessions': attended_sessions,
            'attendance_percentage': round(attendance_percentage, 2),
            'pending_assignments': pending_assignments.count(),
            'latest_grade': latest_grade.grade if latest_grade else None
        })
    
    # Calculate overall attendance
    overall_attendance = (total_attendance_percentage / len(courses)) if courses else 0
    
    # Calculate average grade (just join them with commas for now)
    average_grade = ', '.join(grades) if grades else None
    
    # Get recent notices
    notices = Notice.objects.filter(
        Q(course__in=courses) | Q(course__isnull=True),
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')[:5]
    
    # Get recent assignments
    recent_assignments = Assignment.objects.filter(
        course__in=courses
    ).order_by('-created_at')[:5]
    
    # Get assignment submissions
    submissions = {
        submission.assignment_id: submission
        for submission in AssignmentSubmission.objects.filter(
            student=student,
            assignment__in=recent_assignments
        )
    }
    
    # Get recent resources
    recent_resources = Resource.objects.filter(
        course__in=courses
    ).order_by('-uploaded_at')[:5]
    
    context = {
        'attendance_data': attendance_data,
        'notices': notices,
        'today': date.today(),
        'overall_attendance': overall_attendance,
        'total_pending_assignments': total_pending_assignments,
        'average_grade': average_grade,
        'recent_assignments': recent_assignments,
        'submissions': submissions,
        'recent_resources': recent_resources,
        'total_courses': courses.count()
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def faculty_dashboard(request):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    faculty = request.user.faculty
    courses = Course.objects.filter(faculty=faculty)
    
    # Get recent attendance sessions
    sessions = AttendanceSession.objects.filter(
        course__in=courses
    ).order_by('-date')[:10]
    
    # Get pending assignments to grade
    pending_assignments = Assignment.objects.filter(
        course__in=courses,
        due_date__lt=timezone.now().date()
    ).exclude(submissions__isnull=True, submissions__grade__isnull=False)
    
    # Get recent assignments
    recent_assignments = Assignment.objects.filter(
        course__in=courses
    ).order_by('-created_at')[:5]
    
    # Get recent notices
    recent_notices = Notice.objects.filter(
        Q(course__in=courses) | Q(course__isnull=True),
        created_by=request.user
    ).order_by('-created_at')[:5]
    
    # Get recent resources
    recent_resources = Resource.objects.filter(
        course__in=courses,
        uploaded_by=request.user
    ).order_by('-uploaded_at')[:5]
    
    # Get total students across all courses
    total_students = set()
    for course in courses:
        total_students.update(course.students.all())
    
    # Get course statistics
    course_stats = []
    for course in courses:
        total_students_in_course = course.students.count()
        total_sessions = AttendanceSession.objects.filter(course=course).count()
        
        if total_students_in_course > 0 and total_sessions > 0:
            attendance_percentage = AttendanceRecord.objects.filter(
                session__course=course,
                status=True
            ).count() / (total_sessions * total_students_in_course) * 100
        else:
            attendance_percentage = 0
        
        course_stats.append({
            'course': course,
            'total_students': total_students_in_course,
            'attendance_percentage': round(attendance_percentage, 2),
            'pending_assignments': pending_assignments.filter(course=course).count()
        })
    
    context = {
        'courses': courses,
        'sessions': sessions,
        'course_stats': course_stats,
        'today': date.today(),
        'recent_assignments': recent_assignments,
        'recent_notices': recent_notices,
        'recent_resources': recent_resources,
        'total_students': len(total_students),
        'total_courses': courses.count(),
        'total_sessions': sessions.count(),
        'pending_assignments': pending_assignments.count()
    }
    return render(request, 'faculty/dashboard.html', context)

@login_required
def create_session(request):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        date_str = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        try:
            course = Course.objects.get(id=course_id, faculty=request.user.faculty)
            
            # Create the session
            session = AttendanceSession.objects.create(
                course=course,
                date=date_str,
                start_time=start_time,
                end_time=end_time,
                created_by=request.user.faculty
            )
            
            # If it's an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                students = [{
                    'id': student.id,
                    'name': student.user.get_full_name(),
                    'student_id': student.student_id
                } for student in course.students.all()]
                
                return JsonResponse({
                    'success': True,
                    'session_id': session.id,
                    'students': students
                })
            
            # Otherwise, redirect to mark attendance page
            return redirect('attendance:mark_attendance', session_id=session.id)
            
        except Course.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Course not found'}, status=404)
            messages.error(request, 'Course not found')
            return redirect('attendance:faculty_dashboard')
    
    faculty = request.user.faculty
    courses = Course.objects.filter(faculty=faculty)
    
    context = {
        'courses': courses,
        'today': date.today()
    }
    return render(request, 'faculty/create_session.html', context)

@login_required
def mark_attendance(request, session_id=None):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    # If session_id is provided, show the attendance form for that session
    if session_id:
        try:
            session = AttendanceSession.objects.get(id=session_id)
            course = session.course
            
            # Check if the faculty is assigned to this course
            if course.faculty != request.user.faculty:
                messages.error(request, 'You are not authorized to mark attendance for this session')
                return redirect('attendance:faculty_dashboard')
            
            # Get all students enrolled in the course
            students = course.students.all()
            
            # Get existing attendance records for this session
            attendance_records = {}
            for record in AttendanceRecord.objects.filter(session=session):
                attendance_records[record.student.id] = record.status
            
            if request.method == 'POST':
                # Process the attendance form submission
                for student in students:
                    status = request.POST.get(f'student_{student.id}') == 'present'
                    
                    # Update or create attendance record
                    AttendanceRecord.objects.update_or_create(
                        session=session,
                        student=student,
                        defaults={
                            'status': status,
                            'marked_by': request.user.faculty
                        }
                    )
                
                messages.success(request, 'Attendance marked successfully')
                return redirect('attendance:faculty_dashboard')
            
            context = {
                'session': session,
                'students': students,
                'attendance_records': attendance_records,
                'today': date.today()
            }
            
            return render(request, 'faculty/mark_attendance_session.html', context)
            
        except AttendanceSession.DoesNotExist:
            messages.error(request, 'Session not found')
            return redirect('attendance:faculty_dashboard')
    
    # If no session_id, show the form to create a new session and mark attendance
    faculty = request.user.faculty
    courses = Course.objects.filter(faculty=faculty)
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        date_str = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        try:
            course = Course.objects.get(id=course_id, faculty=faculty)
            
            # Create the session
            session = AttendanceSession.objects.create(
                course=course,
                date=date_str,
                start_time=start_time,
                end_time=end_time,
                created_by=faculty
            )
            
            # If student attendance data is provided
            if 'attendance' in request.POST:
                student_attendance = request.POST.getlist('attendance[]')
                
                # Create attendance records
                for record in student_attendance:
                    student_id, status = record.split('_')
                    student = Student.objects.get(id=student_id)
                    AttendanceRecord.objects.create(
                        session=session,
                        student=student,
                        status=status == 'present',
                        marked_by=faculty
                    )
                
                messages.success(request, 'Attendance marked successfully')
                return redirect('attendance:faculty_dashboard')
            
            # Otherwise, redirect to mark attendance for this session
            return redirect('attendance:mark_attendance', session_id=session.id)
            
        except Course.DoesNotExist:
            messages.error(request, 'Course not found')
            return redirect('attendance:faculty_dashboard')
    
    context = {
        'courses': courses,
        'today': date.today()
    }
    return render(request, 'faculty/mark_attendance.html', context)

@login_required
def view_attendance(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    student = request.user.student
    course_id = request.GET.get('course')
    
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        attendance_records = AttendanceRecord.objects.filter(
            student=student,
            session__course=course
        ).order_by('-session__date')
    else:
        attendance_records = AttendanceRecord.objects.filter(
            student=student
        ).order_by('-session__date')
    
    courses = Course.objects.filter(students=student)
    
    # Calculate attendance statistics
    total_sessions = attendance_records.count()
    present_count = attendance_records.filter(status=True).count()
    absent_count = total_sessions - present_count
    attendance_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0
    
    context = {
        'courses': courses,
        'attendance_records': attendance_records,
        'selected_course_id': course_id,
        'total_sessions': total_sessions,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': round(attendance_percentage, 1)
    }
    return render(request, 'student/view_attendance.html', context)

@login_required
def view_assignments(request, course_id):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    student = request.user.student
    course = get_object_or_404(Course, id=course_id, students=student)
    
    assignments = Assignment.objects.filter(course=course).order_by('-due_date')
    submissions = {
        submission.assignment_id: submission
        for submission in AssignmentSubmission.objects.filter(
            student=student,
            assignment__course=course
        )
    }
    
    context = {
        'course': course,
        'assignments': assignments,
        'submissions': submissions
    }
    return render(request, 'student/view_assignments.html', context)

@login_required
def view_grades(request, course_id):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    student = request.user.student
    course = get_object_or_404(Course, id=course_id, students=student)
    
    grade = Grade.objects.filter(student=student, course=course).first()
    assignments = Assignment.objects.filter(course=course)
    submissions = AssignmentSubmission.objects.filter(
        student=student,
        assignment__course=course
    ).select_related('assignment')
    
    context = {
        'course': course,
        'grade': grade,
        'assignments': assignments,
        'submissions': submissions
    }
    return render(request, 'student/view_grades.html', context)

@login_required
def submit_assignment(request, assignment_id):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    student = request.user.student
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.method == 'POST':
        if 'submission_file' not in request.FILES:
            messages.error(request, 'Please select a file to upload')
            return redirect('attendance:view_assignments', course_id=assignment.course.id)
        
        submission, created = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=student,
            defaults={'submission_file': request.FILES['submission_file']}
        )
        
        if not created:
            submission.submission_file = request.FILES['submission_file']
            submission.submitted_at = timezone.now()
            submission.save()
        
        messages.success(request, 'Assignment submitted successfully')
        return redirect('attendance:view_assignments', course_id=assignment.course.id)
    
    context = {
        'assignment': assignment
    }
    return render(request, 'student/submit_assignment.html', context)

@login_required
def create_assignment(request, course_id):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    faculty = request.user.faculty
    course = get_object_or_404(Course, id=course_id, faculty=faculty)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        max_marks = request.POST.get('max_marks')
        
        Assignment.objects.create(
            course=course,
            title=title,
            description=description,
            due_date=due_date,
            max_marks=max_marks
        )
        
        messages.success(request, 'Assignment created successfully')
        return redirect('attendance:faculty_dashboard')
    
    context = {
        'course': course
    }
    return render(request, 'faculty/create_assignment.html', context)

@login_required
def grade_assignment(request, assignment_id):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    faculty = request.user.faculty
    assignment = get_object_or_404(Assignment, id=assignment_id, course__faculty=faculty)
    
    if request.method == 'POST':
        for submission in assignment.submissions.all():
            grade = request.POST.get(f'grade_{submission.id}')
            remarks = request.POST.get(f'remarks_{submission.id}')
            
            if grade:
                submission.grade = grade
                submission.remarks = remarks
                submission.save()
        
        messages.success(request, 'Grades updated successfully')
        return redirect('attendance:faculty_dashboard')
    
    submissions = assignment.submissions.all()
    context = {
        'assignment': assignment,
        'submissions': submissions
    }
    return render(request, 'faculty/grade_assignment.html', context)

@login_required
def update_grades(request, course_id):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    faculty = request.user.faculty
    course = get_object_or_404(Course, id=course_id, faculty=faculty)
    
    if request.method == 'POST':
        for student in course.students.all():
            grade = request.POST.get(f'grade_{student.id}')
            percentage = request.POST.get(f'percentage_{student.id}')
            remarks = request.POST.get(f'remarks_{student.id}')
            
            if grade and percentage:
                Grade.objects.update_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'grade': grade,
                        'percentage': percentage,
                        'remarks': remarks
                    }
                )
        
        messages.success(request, 'Grades updated successfully')
        return redirect('attendance:faculty_dashboard')
    
    students = course.students.all()
    grades = {
        grade.student_id: grade
        for grade in Grade.objects.filter(course=course)
    }
    
    context = {
        'course': course,
        'students': students,
        'grades': grades
    }
    return render(request, 'faculty/update_grades.html', context)

@login_required
def create_notice(request):
    if request.user.user_type != 'faculty' and not request.user.is_superuser:
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        course_id = request.POST.get('course')
        priority = request.POST.get('priority', 'medium')
        
        notice = Notice.objects.create(
            title=title,
            content=content,
            course_id=course_id if course_id else None,
            created_by=request.user,
            priority=priority
        )
        
        messages.success(request, 'Notice created successfully')
        if request.user.is_superuser:
            return redirect('attendance:admin_dashboard')
        return redirect('attendance:faculty_dashboard')
    
    courses = Course.objects.all()
    if request.user.user_type == 'faculty':
        courses = courses.filter(faculty=request.user.faculty)
    
    context = {
        'courses': courses
    }
    return render(request, 'faculty/create_notice.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    context = {
        'total_students': Student.objects.count(),
        'total_faculty': Faculty.objects.count(),
        'total_courses': Course.objects.count(),
        'recent_notices': Notice.objects.order_by('-created_at')[:5]
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def get_course_students(request, course_id):
    if request.user.user_type != 'faculty':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    course = get_object_or_404(Course, id=course_id, faculty=request.user.faculty)
    students = [{
        'id': student.id,
        'name': f"{student.user.first_name} {student.user.last_name}",
        'student_id': student.student_id
    } for student in course.students.all()]
    
    return JsonResponse({'students': students})

@login_required
def add_student_to_course(request, course_id):
    if request.user.user_type != 'faculty':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    course = get_object_or_404(Course, id=course_id, faculty=request.user.faculty)
    student_id = request.POST.get('student_id')
    
    try:
        student = Student.objects.get(student_id=student_id)
        course.students.add(student)
        return JsonResponse({
            'success': True,
            'student': {
                'id': student.id,
                'name': f"{student.user.first_name} {student.user.last_name}",
                'student_id': student.student_id
            }
        })
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

@login_required
def remove_student_from_course(request, course_id, student_id):
    if request.user.user_type != 'faculty':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    course = get_object_or_404(Course, id=course_id, faculty=request.user.faculty)
    student = get_object_or_404(Student, id=student_id)
    
    course.students.remove(student)
    return JsonResponse({'success': True})

@login_required
def search_students(request):
    if request.user.user_type != 'faculty':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'students': []})
    
    students = Student.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(student_id__icontains=query)
    )[:10]
    
    results = [{
        'id': student.id,
        'name': f"{student.user.first_name} {student.user.last_name}",
        'student_id': student.student_id
    } for student in students]
    
    return JsonResponse({'students': results})

@login_required
def student_attendance_history(request, student_id):
    if request.user.user_type != 'faculty':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    course_id = request.GET.get('course_id')
    if not course_id:
        return JsonResponse({'error': 'Course ID is required'}, status=400)
    
    try:
        student = Student.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        
        # Get the last 10 attendance records for this student in the course
        records = AttendanceRecord.objects.filter(
            student=student,
            session__course=course
        ).order_by('-session__date')[:10]
        
        history = [{
            'date': record.session.date.strftime('%Y-%m-%d'),
            'status': record.status,
            'marked_by': record.marked_by.user.get_full_name() if record.marked_by else 'System',
            'marked_at': record.marked_at.strftime('%Y-%m-%d %H:%M:%S') if record.marked_at else None
        } for record in records]
        
        return JsonResponse({
            'success': True,
            'student_name': student.user.get_full_name(),
            'student_id': student.student_id,
            'course_name': course.name,
            'history': history
        })
    except (Student.DoesNotExist, Course.DoesNotExist):
        return JsonResponse({'error': 'Student or Course not found'}, status=404)

@login_required
def export_attendance(request, session_id):
    if request.user.user_type != 'faculty':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        session = AttendanceSession.objects.get(id=session_id, course__faculty=request.user.faculty)
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_{session.course.code}_{session.date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Name', 'Status', 'Marked By', 'Marked At'])
        
        records = AttendanceRecord.objects.filter(session=session).select_related('student', 'student__user', 'marked_by', 'marked_by__user')
        
        for record in records:
            writer.writerow([
                record.student.student_id,
                record.student.user.get_full_name(),
                'Present' if record.status else 'Absent',
                record.marked_by.user.get_full_name() if record.marked_by else 'System',
                record.marked_at.strftime('%Y-%m-%d %H:%M:%S') if record.marked_at else 'N/A'
            ])
        
        return response
    except AttendanceSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

@login_required
def send_attendance_notifications(request, session_id):
    if request.user.user_type != 'faculty':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        session = AttendanceSession.objects.get(id=session_id, course__faculty=request.user.faculty)
        absent_records = AttendanceRecord.objects.filter(session=session, status=False).select_related('student', 'student__user')
        
        notification_count = 0
        for record in absent_records:
            try:
                send_mail(
                    subject=f'Absence Notification - {session.course.code}',
                    message=f'''Dear {record.student.user.get_full_name()},

This is to inform you that you were marked absent for {session.course.code} - {session.course.name} on {session.date}.

Class Details:
- Date: {session.date}
- Time: {session.start_time} - {session.end_time}
- Faculty: {session.created_by.user.get_full_name()}

Please contact your faculty if you believe this was marked in error.

Best regards,
{settings.COLLEGE_NAME}''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[record.student.user.email],
                )
                notification_count += 1
            except Exception as e:
                print(f"Failed to send email to {record.student.user.email}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'message': f'Sent {notification_count} notification(s)'
        })
    except AttendanceSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

@login_required
def chat_room(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.user_type == 'student' and not course.students.filter(user=request.user).exists():
        messages.error(request, 'Access denied')
        return redirect('attendance:student_dashboard')
    elif request.user.user_type == 'faculty' and course.faculty.user != request.user:
        messages.error(request, 'Access denied')
        return redirect('attendance:faculty_dashboard')
    
    context = {
        'course': course,
        'room_name': f'course_{course_id}',
        'user_full_name': request.user.get_full_name(),
        'user_type': request.user.user_type
    }
    return render(request, 'chat/room.html', context)

@login_required
def upload_resource(request, course_id):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    course = get_object_or_404(Course, id=course_id, faculty=request.user.faculty)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('resource_file')
        
        if not all([title, file]):
            messages.error(request, 'Title and file are required')
            return redirect('attendance:upload_resource', course_id=course_id)
        
        resource = Resource.objects.create(
            course=course,
            title=title,
            description=description,
            file=file,
            uploaded_by=request.user
        )
        
        # Send notification to all students in the course
        students = course.students.all()
        for student in students:
            Notification.objects.create(
                user=student.user,
                title=f'New Resource: {title}',
                message=f'A new resource has been uploaded in {course.code} - {course.name}',
                notification_type='resource',
                related_id=resource.id
            )
        
        messages.success(request, 'Resource uploaded successfully')
        return redirect('attendance:course_resources', course_id=course_id)
    
    context = {
        'course': course
    }
    return render(request, 'faculty/upload_resource.html', context)

@login_required
def course_resources(request, course_id):
    if request.user.user_type == 'student':
        course = get_object_or_404(Course, id=course_id, students=request.user.student)
    else:
        course = get_object_or_404(Course, id=course_id, faculty=request.user.faculty)
    
    resources = Resource.objects.filter(course=course).order_by('-uploaded_at')
    context = {
        'course': course,
        'resources': resources
    }
    return render(request, 'course/resources.html', context)

@login_required
def delete_resource(request, resource_id):
    if request.user.user_type != 'faculty':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    resource = get_object_or_404(Resource, id=resource_id, uploaded_by=request.user)
    resource.delete()
    
    return JsonResponse({'success': True})

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    unread_count = notifications.filter(read=False).count()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'notifications': [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'read': n.read
            } for n in notifications],
            'unread_count': unread_count
        })
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'notifications/list.html', context)

@login_required
def mark_notification_read(request, notification_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    
    return JsonResponse({'success': True})

@login_required
def generate_report(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    report_type = request.GET.get('type')
    course_id = request.GET.get('course')
    
    if report_type == 'attendance':
        course = get_object_or_404(Course, id=course_id)
        records = AttendanceRecord.objects.filter(session__course=course)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{course.code}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Name', 'Total Sessions', 'Present', 'Absent', 'Percentage'])
        
        students = course.students.all()
        for student in students:
            total = records.filter(student=student).count()
            present = records.filter(student=student, status=True).count()
            absent = total - present
            percentage = (present / total * 100) if total > 0 else 0
            
            writer.writerow([
                student.student_id,
                student.user.get_full_name(),
                total,
                present,
                absent,
                f"{percentage:.2f}%"
            ])
        
        return response
    
    elif report_type == 'grades':
        course = get_object_or_404(Course, id=course_id)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="grades_report_{course.code}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Name', 'Grade', 'Percentage', 'Remarks'])
        
        grades = Grade.objects.filter(course=course).select_related('student', 'student__user')
        for grade in grades:
            writer.writerow([
                grade.student.student_id,
                grade.student.user.get_full_name(),
                grade.grade,
                grade.percentage,
                grade.remarks
            ])
        
        return response
    
    elif report_type == 'performance':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="overall_performance_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Name', 'Department', 'Average Grade', 'Overall Attendance', 'Total Courses'])
        
        students = Student.objects.all()
        for student in students:
            grades = Grade.objects.filter(student=student)
            attendance_records = AttendanceRecord.objects.filter(student=student)
            
            total_percentage = sum(float(g.percentage) for g in grades if g.percentage)
            avg_grade = total_percentage / grades.count() if grades.exists() else 0
            
            total_sessions = attendance_records.count()
            present_sessions = attendance_records.filter(status=True).count()
            attendance_percentage = (present_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            writer.writerow([
                student.student_id,
                student.user.get_full_name(),
                student.department,
                f"{avg_grade:.2f}%",
                f"{attendance_percentage:.2f}%",
                student.course_set.count()
            ])
        
        return response
    
    courses = Course.objects.all()
    context = {
        'courses': courses
    }
    return render(request, 'admin/generate_report.html', context)

@login_required
def add_course(request):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        course_name = request.POST.get('course_name')
        description = request.POST.get('description')
        
        if Course.objects.filter(course_code=course_code).exists():
            messages.error(request, 'Course code already exists')
            return redirect('attendance:faculty_dashboard')
        
        course = Course.objects.create(
            course_code=course_code,
            name=course_name,
            description=description,
            faculty=request.user.faculty
        )
        messages.success(request, 'Course added successfully')
        return redirect('attendance:faculty_dashboard')
    
    return render(request, 'faculty/add_course.html')

@login_required
def add_student(request):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('attendance:faculty_dashboard')
        
        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, 'Student ID already exists')
            return redirect('attendance:faculty_dashboard')
        
        # Create user account
        user = User.objects.create_user(
            username=email,
            email=email,
            password=student_id,  # Set initial password as student ID
            first_name=first_name,
            last_name=last_name,
            user_type='student'
        )
        
        # Create student profile
        student = Student.objects.create(
            user=user,
            student_id=student_id
        )
        
        # Add student to course if specified
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                course.students.add(student)
            except Course.DoesNotExist:
                messages.warning(request, 'Course not found')
        
        messages.success(request, 'Student added successfully')
        return redirect('attendance:faculty_dashboard')
    
    courses = Course.objects.filter(faculty=request.user.faculty)
    return render(request, 'faculty/add_student.html', {'courses': courses})

@login_required
def manage_grades(request):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        student_id = request.POST.get('student_id')
        grade_type = request.POST.get('grade_type')
        score = request.POST.get('score')
        
        try:
            course = Course.objects.get(id=course_id)
            student = Student.objects.get(id=student_id)
            
            grade = Grade.objects.create(
                course=course,
                student=student,
                grade_type=grade_type,
                score=score
            )
            
            messages.success(request, 'Grade added successfully')
            return redirect('attendance:faculty_dashboard')
            
        except (Course.DoesNotExist, Student.DoesNotExist):
            messages.error(request, 'Course or student not found')
            return redirect('attendance:faculty_dashboard')
    
    courses = Course.objects.filter(faculty=request.user.faculty)
    return render(request, 'faculty/manage_grades.html', {'courses': courses})

@login_required
def view_course_students(request, course_id):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied')
        return redirect('attendance:login')
    
    try:
        course = Course.objects.get(id=course_id, faculty=request.user.faculty)
        students = course.students.all()
        
        # Get attendance statistics
        attendance_stats = {}
        for student in students:
            total_sessions = AttendanceSession.objects.filter(course=course).count()
            present_sessions = AttendanceRecord.objects.filter(
                session__course=course,
                student=student,
                status=True
            ).count()
            
            attendance_percentage = (present_sessions / total_sessions * 100) if total_sessions > 0 else 0
            attendance_stats[student.id] = round(attendance_percentage, 2)
        
        context = {
            'course': course,
            'students': students,
            'attendance_stats': attendance_stats
        }
        
        return render(request, 'faculty/course_students.html', context)
        
    except Course.DoesNotExist:
        messages.error(request, 'Course not found')
        return redirect('attendance:faculty_dashboard') 