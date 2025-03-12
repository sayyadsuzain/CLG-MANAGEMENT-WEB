// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const ENDPOINTS = {
    profile: `${API_BASE_URL}/users/me/`,
    courses: `${API_BASE_URL}/courses/`,
    attendance: `${API_BASE_URL}/attendance/`,
    assignments: `${API_BASE_URL}/assignments/`,
    grades: `${API_BASE_URL}/grades/`,
    notices: `${API_BASE_URL}/notices/`,
    activities: `${API_BASE_URL}/activities/`,
    students: `${API_BASE_URL}/students/`
};

// Check authentication
function checkAuth() {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        window.location.href = '/index.html';
        return false;
    }
    return true;
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    const accessToken = localStorage.getItem('accessToken');
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
        },
    };

    try {
        const response = await fetch(endpoint, { ...defaultOptions, ...options });
        
        if (response.status === 401) {
            // Token expired or invalid
            localStorage.clear();
            window.location.href = '/index.html';
            return null;
        }

        if (!response.ok) {
            throw new Error(`API request failed: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request error:', error);
        showAlert('Error', error.message);
        return null;
    }
}

// Load user profile and setup UI
async function loadUserProfile() {
    const userData = await apiRequest(ENDPOINTS.profile);
    if (userData) {
        document.getElementById('userFullName').textContent = userData.full_name;
        
        // Show/hide role-specific elements
        const userType = localStorage.getItem('userType');
        document.querySelectorAll('.student-only').forEach(el => {
            el.style.display = userType === 'student' ? '' : 'none';
        });
        document.querySelectorAll('.faculty-only').forEach(el => {
            el.style.display = userType === 'faculty' ? '' : 'none';
        });
    }
}

// Load dashboard statistics
async function loadDashboardStats() {
    const userType = localStorage.getItem('userType');
    
    // Load attendance stats
    const attendance = await apiRequest(ENDPOINTS.attendance);
    if (attendance) {
        const percentage = calculateAttendancePercentage(attendance);
        document.getElementById('attendanceStats').textContent = `${percentage}%`;
    }

    // Load courses
    const courses = await apiRequest(ENDPOINTS.courses);
    if (courses) {
        document.getElementById('coursesStats').textContent = courses.length;
        
        if (userType === 'student') {
            // Calculate CGPA for students
            const grades = await apiRequest(ENDPOINTS.grades);
            if (grades) {
                const cgpa = calculateCGPA(grades);
                document.getElementById('cgpaStats').textContent = cgpa.toFixed(2);
            }
        } else {
            // Show total students for faculty
            const students = await apiRequest(ENDPOINTS.students);
            if (students) {
                document.getElementById('studentsStats').textContent = students.length;
            }
        }
    }

    // Load pending tasks
    const assignments = await apiRequest(ENDPOINTS.assignments);
    if (assignments) {
        const pending = assignments.filter(a => !a.submitted).length;
        document.getElementById('tasksStats').textContent = pending;
    }
}

// Calculate attendance percentage
function calculateAttendancePercentage(attendance) {
    if (!attendance.length) return 0;
    const present = attendance.filter(a => a.status === 'present').length;
    return ((present / attendance.length) * 100).toFixed(1);
}

// Calculate CGPA
function calculateCGPA(grades) {
    if (!grades.length) return 0;
    const gradePoints = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'F': 0.0
    };
    
    const totalPoints = grades.reduce((sum, grade) => sum + (gradePoints[grade.grade] || 0), 0);
    return totalPoints / grades.length;
}

// Load notices
async function loadNotices() {
    const notices = await apiRequest(ENDPOINTS.notices);
    if (notices) {
        const container = document.getElementById('noticeList');
        container.innerHTML = '';

        notices.forEach(notice => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            item.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${notice.title}</h6>
                    <small>${new Date(notice.created_at).toLocaleDateString()}</small>
                </div>
                <p class="mb-1">${notice.content}</p>
                <small>Posted by: ${notice.created_by}</small>
            `;
            container.appendChild(item);
        });
    }
}

// Load activities
async function loadActivities() {
    const activities = await apiRequest(ENDPOINTS.activities);
    if (activities) {
        const container = document.getElementById('activityList');
        container.innerHTML = '';

        activities.slice(0, 5).forEach(activity => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            item.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${activity.type}</h6>
                    <small>${new Date(activity.timestamp).toLocaleDateString()}</small>
                </div>
                <p class="mb-1">${activity.description}</p>
            `;
            container.appendChild(item);
        });
    }
}

// Load deadlines
async function loadDeadlines() {
    const assignments = await apiRequest(ENDPOINTS.assignments);
    if (assignments) {
        const container = document.getElementById('deadlineList');
        container.innerHTML = '';

        assignments
            .filter(a => new Date(a.due_date) > new Date())
            .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
            .slice(0, 5)
            .forEach(assignment => {
                const item = document.createElement('div');
                item.className = 'list-group-item';
                item.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${assignment.title}</h6>
                        <small>${new Date(assignment.due_date).toLocaleDateString()}</small>
                    </div>
                    <p class="mb-1">${assignment.description}</p>
                    <small>Course: ${assignment.course}</small>
                `;
                container.appendChild(item);
            });
    }
}

// Create notice
async function createNotice() {
    const modal = new bootstrap.Modal(document.getElementById('createNoticeModal'));
    modal.show();
}

// Submit notice
async function submitNotice() {
    const title = document.getElementById('noticeTitle').value;
    const content = document.getElementById('noticeContent').value;
    const audience = document.getElementById('noticeAudience').value;

    const response = await apiRequest(ENDPOINTS.notices, {
        method: 'POST',
        body: JSON.stringify({
            title,
            content,
            audience,
            created_by: localStorage.getItem('userId')
        })
    });

    if (response) {
        showAlert('Success', 'Notice created successfully');
        const modal = bootstrap.Modal.getInstance(document.getElementById('createNoticeModal'));
        modal.hide();
        document.getElementById('noticeForm').reset();
        loadNotices(); // Refresh notices
    }
}

// Create assignment
async function createAssignment() {
    // Load courses first
    const courses = await apiRequest(ENDPOINTS.courses);
    if (courses) {
        const courseSelect = document.getElementById('assignmentCourse');
        courseSelect.innerHTML = courses.map(course => 
            `<option value="${course.id}">${course.name}</option>`
        ).join('');
    }

    const modal = new bootstrap.Modal(document.getElementById('createAssignmentModal'));
    modal.show();
}

// Submit assignment
async function submitAssignment() {
    const title = document.getElementById('assignmentTitle').value;
    const description = document.getElementById('assignmentDescription').value;
    const courseId = document.getElementById('assignmentCourse').value;
    const dueDate = document.getElementById('assignmentDueDate').value;
    const marks = document.getElementById('assignmentMarks').value;

    const response = await apiRequest(ENDPOINTS.assignments, {
        method: 'POST',
        body: JSON.stringify({
            title,
            description,
            course_id: courseId,
            due_date: dueDate,
            total_marks: marks,
            created_by: localStorage.getItem('userId')
        })
    });

    if (response) {
        showAlert('Success', 'Assignment created successfully');
        const modal = bootstrap.Modal.getInstance(document.getElementById('createAssignmentModal'));
        modal.hide();
        document.getElementById('assignmentForm').reset();
        loadDeadlines(); // Refresh deadlines
    }
}

// Refresh dashboard data
async function refreshData() {
    await Promise.all([
        loadDashboardStats(),
        loadNotices(),
        loadActivities(),
        loadDeadlines()
    ]);
}

// Show alert helper
function showAlert(title, message) {
    // Implement alert UI (you can use Bootstrap toast or custom alert)
    console.log(`${title}: ${message}`);
}

// Logout function
function logout() {
    localStorage.clear();
    window.location.href = '/index.html';
}

// Initialize dashboard
async function initializeDashboard() {
    if (!checkAuth()) return;

    try {
        await loadUserProfile();
        await refreshData();
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        showAlert('Error', 'Failed to load dashboard data');
    }
}

// Start initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeDashboard); 