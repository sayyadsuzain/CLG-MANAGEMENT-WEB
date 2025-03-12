// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const PROFILE_ENDPOINT = `${API_BASE_URL}/users/profile/`;
const COURSES_ENDPOINT = `${API_BASE_URL}/courses/`;
const ATTENDANCE_ENDPOINT = `${API_BASE_URL}/attendance/`;
const GRADES_ENDPOINT = `${API_BASE_URL}/grades/`;
const ACTIVITIES_ENDPOINT = `${API_BASE_URL}/activities/`;
const NOTICES_ENDPOINT = `${API_BASE_URL}/notices/`;
const DEADLINES_ENDPOINT = `${API_BASE_URL}/deadlines/`;

// Mock data for testing
const MOCK_DATA = {
    profile: {
        full_name: 'Test Student',
        email: 'test@example.com',
        roll_number: 'CS2023001'
    },
    attendance: {
        overall: 85,
        courses: [
            {
                code: 'CS101',
                name: 'Introduction to Programming',
                total_classes: 20,
                attended: 17,
                percentage: 85,
                last_updated: new Date().toISOString(),
                marked_by: 'Dr. Smith'
            },
            {
                code: 'CS102',
                name: 'Data Structures',
                total_classes: 15,
                attended: 13,
                percentage: 87,
                last_updated: new Date().toISOString(),
                marked_by: 'Dr. Johnson'
            }
        ]
    },
    grades: {
        cgpa: 3.75
    },
    courses: [
        {
            code: 'CS101',
            name: 'Introduction to Programming',
            instructor: 'Dr. Smith',
            progress: 75
        },
        {
            code: 'CS102',
            name: 'Data Structures',
            instructor: 'Dr. Johnson',
            progress: 60
        }
    ],
    activities: [
        {
            title: 'Assignment Submitted',
            description: 'Data Structures Assignment 2 submitted',
            timestamp: new Date()
        },
        {
            title: 'Quiz Completed',
            description: 'Scored 90% in Programming Quiz',
            timestamp: new Date()
        }
    ],
    notices: [
        {
            title: 'Exam Schedule',
            content: 'Mid-term exams start from next week',
            date: new Date()
        },
        {
            title: 'Holiday Notice',
            content: 'College will remain closed for festival',
            date: new Date()
        }
    ],
    deadlines: [
        {
            title: 'Programming Assignment',
            description: 'Complete lab exercises',
            course_code: 'CS101',
            due_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000), // 2 days from now
            completed: false
        },
        {
            title: 'Project Submission',
            description: 'Submit project documentation',
            course_code: 'CS102',
            due_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000), // 5 days from now
            completed: false
        }
    ]
};

// Initialize student data
const studentData = {
    courses: JSON.parse(localStorage.getItem('studentCourses') || '[]'),
    messages: JSON.parse(localStorage.getItem('studentMessages') || '[]'),
    feedback: JSON.parse(localStorage.getItem('studentFeedback') || '[]'),
    appointments: JSON.parse(localStorage.getItem('studentAppointments') || '[]')
};

// Load user data from localStorage
const userData = JSON.parse(localStorage.getItem('userData') || '{}');

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing student dashboard...');
    
    if (!checkAuth()) {
        console.log('Auth check failed, stopping initialization');
        return;
    }

    try {
        initializeStudentData();
        setupNavigation();
        loadSection('dashboard');
        console.log('Dashboard initialization complete');
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        showAlert('Error', 'Failed to initialize dashboard data');
    }
});

// Initialize data storage
function initializeStudentData() {
    try {
        // Check authentication
        const accessToken = localStorage.getItem('accessToken');
        const authToken = localStorage.getItem('authToken');
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        
        if ((!accessToken && !authToken) || !userData) {
            window.location.replace('../login.html');
            return;
        }

        // Initialize sample data if not exists
        if (!localStorage.getItem(`courses_${userData.email}`)) {
            const sampleCourses = [
                {
                    id: '1',
                    code: 'CS101',
                    name: 'Introduction to Programming',
                    instructor: 'Dr. Smith',
                    schedule: 'Mon, Wed 10:00 AM',
                    description: 'Basic programming concepts using Python'
                },
                {
                    id: '2',
                    code: 'CS102',
                    name: 'Data Structures',
                    instructor: 'Dr. Johnson',
                    schedule: 'Tue, Thu 2:00 PM',
                    description: 'Advanced data structures and algorithms'
                }
            ];
            localStorage.setItem(`courses_${userData.email}`, JSON.stringify(sampleCourses));

            // Initialize attendance data
            sampleCourses.forEach(course => {
                const attendanceKey = `attendance_${userData.email}_${course.id}`;
                const sampleAttendance = Array.from({length: 20}, (_, i) => ({
                    date: new Date(Date.now() - (i * 24 * 60 * 60 * 1000)).toISOString(),
                    present: Math.random() > 0.2,
                    markedBy: course.instructor,
                    markedAt: new Date(Date.now() - (i * 24 * 60 * 60 * 1000)).toISOString()
                }));
                localStorage.setItem(attendanceKey, JSON.stringify(sampleAttendance));
            });

            // Initialize assignments data
            sampleCourses.forEach(course => {
                const assignmentsKey = `assignments_${course.id}`;
                const sampleAssignments = [
                    {
                        id: `${course.id}_1`,
                        title: 'Assignment 1',
                        description: 'First assignment for ' + course.name,
                        dueDate: new Date(Date.now() + (7 * 24 * 60 * 60 * 1000)).toISOString(),
                        submissions: {
                            [userData.email]: {
                                submittedAt: new Date(Date.now() - (2 * 24 * 60 * 60 * 1000)).toISOString(),
                                score: Math.floor(Math.random() * 20 + 80)
                            }
                        }
                    },
                    {
                        id: `${course.id}_2`,
                        title: 'Assignment 2',
                        description: 'Second assignment for ' + course.name,
                        dueDate: new Date(Date.now() + (14 * 24 * 60 * 60 * 1000)).toISOString(),
                        submissions: {}
                    }
                ];
                localStorage.setItem(assignmentsKey, JSON.stringify(sampleAssignments));
            });

            // Initialize grades data
            sampleCourses.forEach(course => {
                const gradeKey = `grades_${userData.email}_${course.id}`;
                const sampleGrade = {
                    score: Math.floor(Math.random() * 20 + 80),
                    details: [
                        {
                            component: 'Assignments',
                            score: Math.floor(Math.random() * 20 + 80),
                            weight: 30
                        },
                        {
                            component: 'Mid-term',
                            score: Math.floor(Math.random() * 20 + 80),
                            weight: 30
                        },
                        {
                            component: 'Final Exam',
                            score: Math.floor(Math.random() * 20 + 80),
                            weight: 40
                        }
                    ]
                };
                localStorage.setItem(gradeKey, JSON.stringify(sampleGrade));
            });
        }

        // Update UI with user info
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = userData.full_name || 'Student';
        }

        // Initialize attendance data
        initializeAttendanceData();

    } catch (error) {
        console.error('Error initializing student data:', error);
        showAlert('Error', 'Failed to initialize dashboard data');
    }
}

// Initialize attendance data structure
function initializeAttendanceData() {
    try {
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        const courses = JSON.parse(localStorage.getItem(`courses_${userData.email}`) || '[]');
        
        courses.forEach(course => {
            const attendanceKey = `attendance_${course.id}`;
            if (!localStorage.getItem(attendanceKey)) {
                const attendanceData = {
                    courseId: course.id,
                    courseName: course.name,
                    studentEmail: userData.email,
                    facultyEmail: course.facultyEmail,
                    records: []
                };
                localStorage.setItem(attendanceKey, JSON.stringify(attendanceData));
            }
        });
    } catch (error) {
        console.error('Error initializing attendance data:', error);
    }
}

// Setup navigation
function setupNavigation() {
    const sideNav = document.getElementById('sideNav');
    if (!sideNav) return;

    sideNav.addEventListener('click', async (e) => {
        e.preventDefault();
        
        const link = e.target.closest('.nav-link');
        if (!link) return;

        const section = link.dataset.section;
        if (!section) return;

        // Update active state
        document.querySelectorAll('.nav-link').forEach(navLink => {
            navLink.classList.remove('active');
        });
        link.classList.add('active');

        // Load section content
        await loadSection(section);
    });
}

// Load section content
async function loadSection(section) {
    try {
        const mainContent = document.getElementById('mainContent');
        if (!mainContent) {
            console.error('Main content container not found');
            return;
        }

        console.log('Loading section:', section);

        // Generate content based on section
        const content = generateSectionContent(section);
        
        // Display content
        mainContent.innerHTML = content;
        
        // Setup event listeners for the new content
        setupSectionEventListeners(section);
        
    } catch (error) {
        console.error('Error loading section:', error);
        const mainContent = document.getElementById('mainContent');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="alert alert-danger">
                    Error loading content. Please try refreshing the page.
                </div>
            `;
        }
    }
}

// Generate section content
function generateSectionContent(section) {
    switch (section) {
        case 'dashboard':
            return generateDashboardContent();
        case 'courses':
            return generateCoursesContent();
        case 'messages':
            return generateMessagesContent();
        case 'appointments':
            return generateAppointmentsContent();
        default:
            return `
                <div class="container py-4">
                    <div class="alert alert-warning">
                        Section "${section}" not found
                    </div>
                </div>
            `;
    }
}

// Generate dashboard content
function generateDashboardContent() {
    return `
        <div class="container py-4">
            <!-- Welcome Card -->
            <div class="card mb-4">
                <div class="card-body">
                    <h4>Welcome, ${userData.full_name || 'Student'}!</h4>
                    <p>Here's your academic overview</p>
                </div>
            </div>

            <!-- Quick Stats -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Courses</h5>
                            <p class="h2 mb-0">${studentData.courses.length}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Messages</h5>
                            <p class="h2 mb-0">${getUnreadMessagesCount()}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Appointments</h5>
                            <p class="h2 mb-0">${getUpcomingAppointmentsCount()}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Average Grade</h5>
                            <p class="h2 mb-0">${calculateAverageGrade()}%</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Faculty Interactions -->
            <div class="row">
                <!-- Recent Messages -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Recent Messages</h5>
                            <button class="btn btn-sm btn-primary" onclick="showNewMessageModal()">
                                New Message
                            </button>
                        </div>
                        <div class="card-body">
                            ${getRecentMessages()}
                        </div>
                    </div>
                </div>

                <!-- Upcoming Appointments -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Upcoming Appointments</h5>
                            <button class="btn btn-sm btn-primary" onclick="showBookAppointmentModal()">
                                Book Appointment
                            </button>
                        </div>
                        <div class="card-body">
                            ${getUpcomingAppointments()}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Generate messages content
function generateMessagesContent() {
    return `
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Messages</h2>
                <button class="btn btn-primary" onclick="showNewMessageModal()">
                    <i class="fas fa-plus"></i> New Message
                </button>
            </div>

            <div class="row">
                <!-- Message List -->
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Conversations</h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="list-group list-group-flush">
                                ${getMessageThreads()}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Message Content -->
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0" id="currentThreadTitle">Select a conversation</h5>
                        </div>
                        <div class="card-body" id="messageContent">
                            <p class="text-muted text-center">Select a conversation to view messages</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Generate appointments content
function generateAppointmentsContent() {
    return `
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Faculty Appointments</h2>
                <button class="btn btn-primary" onclick="showBookAppointmentModal()">
                    <i class="fas fa-plus"></i> Book Appointment
                </button>
            </div>

            <!-- Available Office Hours -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Available Office Hours</h5>
                </div>
                <div class="card-body">
                    ${getAvailableOfficeHours()}
                </div>
            </div>

            <!-- My Appointments -->
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">My Appointments</h5>
                </div>
                <div class="card-body">
                    ${getMyAppointments()}
                </div>
            </div>
        </div>
    `;
}

// Generate courses content
function generateCoursesContent() {
    const courses = JSON.parse(localStorage.getItem(`courses_${userData.email}`) || '[]');
    
    return `
        <div class="container py-4">
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">My Courses</h5>
                </div>
                <div class="card-body">
                    ${courses.length > 0 ? `
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Course Code</th>
                                        <th>Course Name</th>
                                        <th>Instructor</th>
                                        <th>Attendance</th>
                                        <th>Assignments</th>
                                        <th>Grade</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${courses.map(course => {
                                        const attendance = getAttendanceForCourse(course.id);
                                        const assignments = getAssignmentsForCourse(course.id);
                                        const grade = getGradeForCourse(course.id);
                                        
                                        return `
                                            <tr>
                                                <td>${course.code}</td>
                                                <td>${course.name}</td>
                                                <td>${course.instructor}</td>
                                                <td>
                                                    <div class="progress" style="height: 20px;">
                                                        <div class="progress-bar ${attendance.percentage >= 75 ? 'bg-success' : 'bg-warning'}" 
                                                            role="progressbar" 
                                                            style="width: ${attendance.percentage}%">
                                                            ${attendance.percentage}%
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>
                                                    ${assignments.completed}/${assignments.total} Done
                                                </td>
                                                <td>
                                                    <span class="badge bg-${getGradeBadgeColor(grade.score)}">
                                                        ${grade.score || 'N/A'}
                                                    </span>
                                                </td>
                                                <td>
                                                    <button class="btn btn-sm btn-primary" onclick="viewCourseDetails('${course.id}')">
                                                        View Details
                                                    </button>
                                                </td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    ` : '<p class="text-muted">No courses assigned yet.</p>'}
                </div>
            </div>
        </div>
    `;
}

// Function to get attendance for a specific course
function getAttendanceForCourse(courseId) {
    try {
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        const currentFaculty = JSON.parse(localStorage.getItem('currentFaculty') || '{}');
        const attendanceKey = `attendance_${courseId}`;
        const attendanceData = JSON.parse(localStorage.getItem(attendanceKey) || '{}');
        
        // Filter only attendance marked by current faculty using email
        const markedAttendance = (attendanceData.records || []).filter(record => 
            record.markedByEmail && 
            record.markedByEmail === currentFaculty.email
        );
        
        const totalClasses = markedAttendance.length;
        const attendedClasses = markedAttendance.filter(record => record.present).length;
        const percentage = totalClasses > 0 ? Math.round((attendedClasses / totalClasses) * 100) : 0;
        
        // Get the last marking details
        const lastMarked = markedAttendance.length > 0 ? markedAttendance[markedAttendance.length - 1] : null;
        
        return {
            total: totalClasses,
            attended: attendedClasses,
            percentage: percentage,
            lastUpdated: lastMarked ? lastMarked.markedAt : null,
            lastMarkedBy: lastMarked ? lastMarked.markedByName : null,
            lastMarkedByEmail: lastMarked ? lastMarked.markedByEmail : null,
            records: markedAttendance.map(record => ({
                ...record,
                date: new Date(record.date),
                markedAt: new Date(record.markedAt)
            }))
        };
    } catch (error) {
        console.error('Error getting attendance for course:', error);
        return {
            total: 0,
            attended: 0,
            percentage: 0,
            lastUpdated: null,
            lastMarkedBy: null,
            lastMarkedByEmail: null,
            records: []
        };
    }
}

// Function to get assignments for a specific course
function getAssignmentsForCourse(courseId) {
    const assignmentsKey = `assignments_${courseId}`;
    const assignments = JSON.parse(localStorage.getItem(assignmentsKey) || '[]');
    const studentAssignments = assignments.filter(assignment => 
        assignment.submissions && assignment.submissions[userData.email]
    );
    
    return {
        total: assignments.length,
        completed: studentAssignments.length,
        assignments: assignments
    };
}

// Function to get grade for a specific course
function getGradeForCourse(courseId) {
    const gradeKey = `grades_${userData.email}_${courseId}`;
    const grade = JSON.parse(localStorage.getItem(gradeKey) || '{}');
    
    return {
        score: grade.score || 'N/A',
        details: grade.details || []
    };
}

// Function to view course details
function viewCourseDetails(courseId) {
    const course = JSON.parse(localStorage.getItem(`courses_${userData.email}`))
        .find(c => c.id === courseId);
    const attendance = getAttendanceForCourse(courseId);
    const assignments = getAssignmentsForCourse(courseId);
    const grade = getGradeForCourse(courseId);
    
    const modalHtml = `
        <div class="modal fade" id="courseDetailsModal">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${course.code} - ${course.name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Course Info -->
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6>Course Information</h6>
                                <p><strong>Instructor:</strong> ${course.instructor}</p>
                                <p><strong>Schedule:</strong> ${course.schedule || 'Not specified'}</p>
                                <p><strong>Description:</strong> ${course.description || 'No description available'}</p>
                            </div>
                        </div>

                        <!-- Attendance -->
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6>Attendance</h6>
                                <div class="progress mb-2" style="height: 20px;">
                                    <div class="progress-bar ${attendance.percentage >= 75 ? 'bg-success' : 'bg-warning'}" 
                                        role="progressbar" 
                                        style="width: ${attendance.percentage}%">
                                        ${attendance.percentage}%
                                    </div>
                                </div>
                                <p>Classes Attended: ${attendance.attended}/${attendance.total}</p>
                            </div>
                        </div>

                        <!-- Assignments -->
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6>Assignments</h6>
                                <div class="table-responsive">
                                    <table class="table">
                                        <thead>
                                            <tr>
                                                <th>Title</th>
                                                <th>Due Date</th>
                                                <th>Status</th>
                                                <th>Score</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${assignments.assignments.map(assignment => {
                                                const submission = assignment.submissions?.[userData.email];
                                                return `
                                                    <tr>
                                                        <td>${assignment.title}</td>
                                                        <td>${new Date(assignment.dueDate).toLocaleDateString()}</td>
                                                        <td>
                                                            <span class="badge bg-${submission ? 'success' : 'warning'}">
                                                                ${submission ? 'Submitted' : 'Pending'}
                                                            </span>
                                                        </td>
                                                        <td>${submission?.score || 'N/A'}</td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <!-- Grades -->
                        <div class="card">
                            <div class="card-body">
                                <h6>Grades</h6>
                                <div class="table-responsive">
                                    <table class="table">
                                        <thead>
                                            <tr>
                                                <th>Component</th>
                                                <th>Score</th>
                                                <th>Weight</th>
                                                <th>Weighted Score</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${grade.details.map(detail => `
                                                <tr>
                                                    <td>${detail.component}</td>
                                                    <td>${detail.score}</td>
                                                    <td>${detail.weight}%</td>
                                                    <td>${(detail.score * detail.weight / 100).toFixed(2)}</td>
                                                </tr>
                                            `).join('')}
                                            <tr class="table-active">
                                                <td colspan="3"><strong>Final Grade</strong></td>
                                                <td><strong>${grade.score || 'N/A'}</strong></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('courseDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add new modal to the document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('courseDetailsModal'));
    modal.show();
}

// Helper functions
function getUnreadMessagesCount() {
    return studentData.messages.filter(msg => !msg.read).length;
}

function getUpcomingAppointmentsCount() {
    const now = new Date();
    return studentData.appointments.filter(apt => new Date(apt.date) > now).length;
}

function calculateAverageGrade() {
    if (studentData.courses.length === 0) return 0;
    
    const totalGrades = studentData.courses.reduce((sum, course) => {
        return sum + (course.grade || 0);
    }, 0);
    
    return Math.round(totalGrades / studentData.courses.length);
}

function getRecentMessages() {
    const messages = studentData.messages.slice(0, 5);
    if (messages.length === 0) {
        return '<p class="text-muted">No recent messages</p>';
    }

    return `
        <div class="messages-list">
            ${messages.map(msg => `
                <div class="message-item mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <h6 class="mb-1">${msg.sender}</h6>
                        <small class="text-muted">${new Date(msg.timestamp).toLocaleString()}</small>
                    </div>
                    <p class="mb-1">${msg.content}</p>
                </div>
            `).join('')}
        </div>
    `;
}

function getUpcomingAppointments() {
    const now = new Date();
    const appointments = studentData.appointments
        .filter(apt => new Date(apt.date) > now)
        .slice(0, 5);

    if (appointments.length === 0) {
        return '<p class="text-muted">No upcoming appointments</p>';
    }

    return `
        <div class="appointments-list">
            ${appointments.map(apt => `
                <div class="appointment-item mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <h6 class="mb-1">${apt.facultyName}</h6>
                        <small class="text-muted">${new Date(apt.date).toLocaleString()}</small>
                    </div>
                    <p class="mb-1">${apt.purpose}</p>
                    <small class="text-muted">Location: ${apt.location}</small>
                </div>
            `).join('')}
        </div>
    `;
}

function getMessageThreads() {
    if (studentData.messages.length === 0) {
        return '<div class="list-group-item">No messages</div>';
    }

    // Group messages by faculty
    const threads = studentData.messages.reduce((acc, msg) => {
        if (!acc[msg.sender]) {
            acc[msg.sender] = [];
        }
        acc[msg.sender].push(msg);
        return acc;
    }, {});

    return Object.entries(threads).map(([sender, messages]) => `
        <a href="#" class="list-group-item list-group-item-action" 
            onclick="showMessageThread('${sender}')">
            <div class="d-flex justify-content-between align-items-center">
                <h6 class="mb-1">${sender}</h6>
                <small class="text-muted">${new Date(messages[0].timestamp).toLocaleString()}</small>
            </div>
            <p class="mb-1 text-truncate">${messages[0].content}</p>
            ${messages.some(msg => !msg.read) ? 
                '<span class="badge bg-primary">New</span>' : ''}
        </a>
    `).join('');
}

function getAvailableOfficeHours() {
    const officeHours = JSON.parse(localStorage.getItem('facultyOfficeHours') || '[]');
    if (officeHours.length === 0) {
        return '<p class="text-muted">No office hours available</p>';
    }

    return `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Faculty</th>
                        <th>Day</th>
                        <th>Time</th>
                        <th>Location</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${officeHours.filter(hour => hour.isAvailable).map(hour => `
                        <tr>
                            <td>${hour.facultyName}</td>
                            <td>${hour.day}</td>
                            <td>${hour.startTime} - ${hour.endTime}</td>
                            <td>${hour.location}</td>
                            <td>
                                <button class="btn btn-sm btn-primary" 
                                    onclick="bookAppointment('${hour.id}')">
                                    Book
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function getMyAppointments() {
    if (studentData.appointments.length === 0) {
        return '<p class="text-muted">No appointments scheduled</p>';
    }

    return `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Faculty</th>
                        <th>Date & Time</th>
                        <th>Location</th>
                        <th>Purpose</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${studentData.appointments.map(apt => `
                        <tr>
                            <td>${apt.facultyName}</td>
                            <td>${new Date(apt.date).toLocaleString()}</td>
                            <td>${apt.location}</td>
                            <td>${apt.purpose}</td>
                            <td>
                                <span class="badge bg-${getAppointmentStatusColor(apt.status)}">
                                    ${apt.status}
                                </span>
                            </td>
                            <td>
                                ${apt.status === 'scheduled' ? `
                                    <button class="btn btn-sm btn-danger" 
                                        onclick="cancelAppointment('${apt.id}')">
                                        Cancel
                                    </button>
                                ` : ''}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Modal functions
function showNewMessageModal() {
    const modalHtml = `
        <div class="modal fade" id="newMessageModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">New Message</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="newMessageForm">
                            <div class="mb-3">
                                <label class="form-label">Faculty</label>
                                <select class="form-select" name="faculty" required>
                                    <option value="">Select Faculty</option>
                                    ${getFacultyOptions()}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Subject</label>
                                <input type="text" class="form-control" name="subject" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Message</label>
                                <textarea class="form-control" name="message" rows="4" required></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('newMessageModal'));
    modal.show();
}

function showBookAppointmentModal() {
    const modalHtml = `
        <div class="modal fade" id="bookAppointmentModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Book Appointment</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="bookAppointmentForm">
                            <div class="mb-3">
                                <label class="form-label">Faculty</label>
                                <select class="form-select" name="faculty" required onchange="loadFacultyOfficeHours()">
                                    <option value="">Select Faculty</option>
                                    ${getFacultyOptions()}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Available Slots</label>
                                <select class="form-select" name="slot" required>
                                    <option value="">Select Time Slot</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Purpose</label>
                                <textarea class="form-control" name="purpose" rows="3" required></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="bookAppointment()">Book</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('bookAppointmentModal'));
    modal.show();
}

// Action functions
function sendMessage() {
    const form = document.getElementById('newMessageForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const message = {
        id: Date.now().toString(),
        sender: userData.full_name,
        recipient: formData.get('faculty'),
        subject: formData.get('subject'),
        content: formData.get('message'),
        timestamp: new Date().toISOString(),
        read: false
    };

    // Save to localStorage
    studentData.messages.unshift(message);
    localStorage.setItem('studentMessages', JSON.stringify(studentData.messages));

    // Close modal and refresh
    const modal = bootstrap.Modal.getInstance(document.getElementById('newMessageModal'));
    modal.hide();
    showAlert('Success', 'Message sent successfully');
    loadSection('messages');
}

function bookAppointment() {
    const form = document.getElementById('bookAppointmentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const appointment = {
        id: Date.now().toString(),
        studentId: userData.id,
        studentName: userData.full_name,
        facultyName: formData.get('faculty'),
        date: formData.get('slot'),
        purpose: formData.get('purpose'),
        status: 'pending',
        createdAt: new Date().toISOString()
    };

    // Save to localStorage
    studentData.appointments.push(appointment);
    localStorage.setItem('studentAppointments', JSON.stringify(studentData.appointments));

    // Close modal and refresh
    const modal = bootstrap.Modal.getInstance(document.getElementById('bookAppointmentModal'));
    modal.hide();
    showAlert('Success', 'Appointment request sent successfully');
    loadSection('appointments');
}

function cancelAppointment(appointmentId) {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        const index = studentData.appointments.findIndex(apt => apt.id === appointmentId);
        if (index !== -1) {
            studentData.appointments[index].status = 'cancelled';
            localStorage.setItem('studentAppointments', JSON.stringify(studentData.appointments));
            loadSection('appointments');
            showAlert('Success', 'Appointment cancelled successfully');
        }
    }
}

// Utility functions
function getFacultyOptions() {
    const faculty = JSON.parse(localStorage.getItem('facultyList') || '[]');
    return faculty.map(f => `
        <option value="${f.id}">${f.name} (${f.department})</option>
    `).join('');
}

function getAppointmentStatusColor(status) {
    const colors = {
        pending: 'warning',
        scheduled: 'success',
        cancelled: 'danger',
        completed: 'info'
    };
    return colors[status] || 'secondary';
}

function showAlert(title, message) {
    const alertHtml = `
        <div class="alert alert-info alert-dismissible fade show" role="alert">
            <strong>${title}:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const alertContainer = document.getElementById('alertContainer') || document.createElement('div');
    alertContainer.id = 'alertContainer';
    alertContainer.style.position = 'fixed';
    alertContainer.style.top = '20px';
    alertContainer.style.right = '20px';
    alertContainer.style.zIndex = '9999';
    
    document.body.appendChild(alertContainer);
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    setTimeout(() => {
        const alerts = alertContainer.getElementsByClassName('alert');
        if (alerts.length > 0) {
            alerts[0].remove();
        }
    }, 5000);
}

// Function to get student's assigned courses
async function getStudentCourses() {
    // In a real app, this would be an API call
    // For now, we'll get it from localStorage
    return JSON.parse(localStorage.getItem(`courses_${studentEmail}`) || '[]');
}

// Function to get student's attendance
async function getStudentAttendance() {
    const courses = await getStudentCourses();
    const attendance = [];
    
    for (const course of courses) {
        const attendanceKey = `attendance_${studentEmail}_${course.id}`;
        const courseAttendance = JSON.parse(localStorage.getItem(attendanceKey) || '[]');
        attendance.push({
            courseCode: course.code,
            courseName: course.name,
            attendance: courseAttendance
        });
    }
    
    return attendance;
}

// Check if user is authenticated
function checkAuth() {
    console.log('Checking dashboard authentication...'); // Debug log
    const accessToken = localStorage.getItem('accessToken');
    const authToken = localStorage.getItem('authToken'); // For backward compatibility
    const userType = localStorage.getItem('userType');
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');

    console.log('Auth state:', { 
        accessToken: !!accessToken, 
        authToken: !!authToken,
        userType, 
        userData 
    }); // Debug log

    // Check for either token type and correct user type
    if ((!accessToken && !authToken) || userType !== 'student' || !userData) {
        console.log('Authentication failed, redirecting to login...'); // Debug log
        window.location.href = '../login.html';
        return false;
    }

    // Update UI with user info
    const studentName = document.getElementById('studentName');
    if (studentName && userData.full_name) {
        studentName.textContent = `Welcome, ${userData.full_name}`;
    }

    console.log('Authentication successful'); // Debug log
    return true;
}

// Helper function for API requests
async function apiRequest(endpoint, options = {}) {
    const accessToken = localStorage.getItem('accessToken');
    console.log(`Making API request to: ${endpoint}`); // Debug log
    
    try {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`,
                ...options.headers,
            },
        });

        console.log(`API response status: ${response.status}`); // Debug log

        if (response.status === 401) {
            console.log('Token expired or invalid, redirecting to login...'); // Debug log
            localStorage.clear();
            window.location.href = '../login.html';
            return null;
        }

        if (!response.ok) {
            throw new Error(`API request failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('API response data:', data); // Debug log
        return data;
    } catch (error) {
        console.error('API request error:', error);
        return null;
    }
}

// Load user profile
async function loadUserProfile() {
    document.getElementById('userFullName').textContent = MOCK_DATA.profile.full_name;
}

// Load attendance data with real-time updates
async function loadAttendanceData() {
    try {
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        const currentFaculty = JSON.parse(localStorage.getItem('currentFaculty') || '{}');
        const courses = JSON.parse(localStorage.getItem(`courses_${userData.email}`) || '[]');
        
        // Filter courses taught by current faculty using email
        const facultyCourses = courses.filter(course => course.facultyEmail === currentFaculty.email);
        
        // Update attendance table
        const attendanceTable = document.getElementById('attendanceDetails');
        if (!attendanceTable) {
            console.error('Attendance table element not found');
            return;
        }

        const tbody = attendanceTable.querySelector('tbody') || attendanceTable;
        tbody.innerHTML = facultyCourses.map(course => {
            const attendance = getAttendanceForCourse(course.id);
            
            return `
                <tr>
                    <td>${course.code}</td>
                    <td>${course.name}</td>
                    <td>${attendance.attended}/${attendance.total}</td>
                    <td>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar ${attendance.percentage >= 75 ? 'bg-success' : 'bg-warning'}" 
                                role="progressbar" 
                                style="width: ${attendance.percentage}%">
                                ${attendance.percentage}%
                            </div>
                        </div>
                    </td>
                    <td>
                        ${attendance.lastMarkedBy ? `
                            <div>
                                <small>Last marked by: ${attendance.lastMarkedBy}</small><br>
                                <small>Email: ${attendance.lastMarkedByEmail}</small><br>
                                <small>Date: ${new Date(attendance.lastUpdated).toLocaleDateString()}</small>
                            </div>
                        ` : '<small class="text-muted">No attendance marked yet</small>'}
                    </td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="viewAttendanceDetails('${course.id}')">
                            View Details
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        // Show message if no courses found
        if (facultyCourses.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">
                        <p class="text-muted">No courses found for current faculty</p>
                    </td>
                </tr>
            `;
        }

        // Setup WebSocket connection for real-time updates
        setupAttendanceWebSocket(userData.email);

    } catch (error) {
        console.error('Error loading attendance data:', error);
        showAlert('Error', 'Failed to load attendance data. Please try refreshing the page.');
    }
}

// Setup WebSocket for real-time attendance updates
function setupAttendanceWebSocket(studentEmail) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/attendance/${studentEmail}/`;
    
    const socket = new WebSocket(wsUrl);
    
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'attendance_update') {
            // Refresh attendance data when update received
            loadAttendanceData();
            showAlert('Update', 'Attendance has been updated by faculty');
        }
    };
    
    socket.onclose = () => {
        console.log('WebSocket connection closed. Retrying in 5 seconds...');
        setTimeout(() => setupAttendanceWebSocket(studentEmail), 5000);
    };
}

// Function to view detailed attendance records
function viewAttendanceDetails(courseId) {
    const course = JSON.parse(localStorage.getItem(`courses_${userData.email}`))
        .find(c => c.id === courseId);
    const attendance = getAttendanceForCourse(courseId);
    const currentFaculty = JSON.parse(localStorage.getItem('currentFaculty') || '{}');
    
    const modalHtml = `
        <div class="modal fade" id="attendanceDetailsModal">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Attendance Details - ${course.code}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6>Course Information</h6>
                                <p><strong>Course:</strong> ${course.name}</p>
                                <p><strong>Faculty:</strong> ${currentFaculty.name}</p>
                                <p><strong>Faculty Email:</strong> ${currentFaculty.email}</p>
                                <p><strong>Overall Attendance:</strong> ${attendance.percentage}%</p>
                            </div>
                        </div>
                        
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Status</th>
                                        <th>Marked By</th>
                                        <th>Faculty Email</th>
                                        <th>Marked On</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${attendance.records.length > 0 ? 
                                        attendance.records.map(record => `
                                            <tr>
                                                <td>${record.date.toLocaleDateString()}</td>
                                                <td>
                                                    <span class="badge bg-${record.present ? 'success' : 'danger'}">
                                                        ${record.present ? 'Present' : 'Absent'}
                                                    </span>
                                                </td>
                                                <td>${record.markedByName}</td>
                                                <td>${record.markedByEmail}</td>
                                                <td>${record.markedAt.toLocaleString()}</td>
                                            </tr>
                                        `).join('') : 
                                        `<tr>
                                            <td colspan="5" class="text-center">
                                                <p class="text-muted">No attendance records found</p>
                                            </td>
                                        </tr>`
                                    }
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('attendanceDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add new modal to the document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('attendanceDetailsModal'));
    modal.show();
}

// Load dashboard statistics
async function loadDashboardStats() {
    // Load attendance
    document.getElementById('attendancePercentage').textContent = `${MOCK_DATA.attendance.percentage}%`;

    // Load CGPA
    document.getElementById('cgpaValue').textContent = MOCK_DATA.grades.cgpa.toFixed(2);

    // Load courses count
    document.getElementById('coursesCount').textContent = MOCK_DATA.courses.length;
    loadCourseTable(MOCK_DATA.courses);

    // Load pending tasks
    const pending = MOCK_DATA.deadlines.filter(task => !task.completed).length;
    document.getElementById('pendingTasks').textContent = pending;
}

// Load course table
function loadCourseTable(courses) {
    const tableBody = document.querySelector('#coursesTable tbody');
    tableBody.innerHTML = '';

    courses.forEach(course => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${course.code}</td>
            <td>${course.name}</td>
            <td>${course.instructor}</td>
            <td>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width: ${course.progress}%">
                        ${course.progress}%
                    </div>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Load recent activities
async function loadActivities() {
    const activityList = document.getElementById('activitiesList');
    activityList.innerHTML = '';

    MOCK_DATA.activities.forEach(activity => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action';
        item.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${activity.title}</h6>
                <small>${new Date(activity.timestamp).toLocaleDateString()}</small>
            </div>
            <p class="mb-1">${activity.description}</p>
        `;
        activityList.appendChild(item);
    });
}

// Load notices
async function loadNotices() {
    const noticesList = document.getElementById('noticesList');
    noticesList.innerHTML = '';

    MOCK_DATA.notices.forEach(notice => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action';
        item.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${notice.title}</h6>
                <small>${new Date(notice.date).toLocaleDateString()}</small>
            </div>
            <p class="mb-1">${notice.content}</p>
        `;
        noticesList.appendChild(item);
    });
}

// Load deadlines
async function loadDeadlines() {
    const deadlinesList = document.getElementById('deadlinesList');
    deadlinesList.innerHTML = '';

    MOCK_DATA.deadlines.forEach(deadline => {
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action';
        const dueDate = new Date(deadline.due_date);
        const today = new Date();
        const daysLeft = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
        
        item.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${deadline.title}</h6>
                <small>${daysLeft <= 3 ? 'text-danger' : 'text-muted'}">
                    Due in ${daysLeft} days
                </small>
            </div>
            <p class="mb-1">${deadline.description}</p>
            <small>${deadline.course_code}</small>
        `;
        deadlinesList.appendChild(item);
    });
}

// Handle logout
function logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userType');
    localStorage.removeItem('userData');
    window.location.href = '../login.html';
}

// Helper functions
async function getStudentAssignments() {
    const courses = await getStudentCourses();
    let assignments = [];
    
    for (const course of courses) {
        const courseAssignments = JSON.parse(localStorage.getItem(`assignments_${course.id}`) || '[]');
        assignments = assignments.concat(courseAssignments.map(assignment => ({
            ...assignment,
            courseCode: course.code
        })));
    }
    
    return assignments;
}

async function getStudentGrades() {
    const courses = await getStudentCourses();
    const grades = {};
    
    for (const course of courses) {
        const gradeKey = `grades_${studentEmail}_${course.id}`;
        const courseGrades = JSON.parse(localStorage.getItem(gradeKey) || '{}');
        if (Object.keys(courseGrades).length > 0) {
            grades[course.code] = courseGrades;
        }
    }
    
    return grades;
}

function getGradeBadgeColor(grade) {
    if (!grade) return 'secondary';
    if (grade >= 90) return 'success';
    if (grade >= 80) return 'primary';
    if (grade >= 70) return 'info';
    if (grade >= 60) return 'warning';
    return 'danger';
}

// Refresh functions
async function refreshAttendance() {
    try {
        await loadAttendanceData();
        showAlert('Success', 'Attendance data refreshed successfully');
    } catch (error) {
        console.error('Error refreshing attendance:', error);
        showAlert('Error', 'Failed to refresh attendance data');
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Initializing student dashboard...');
    
    if (!checkAuth()) {
        console.log('Auth check failed, stopping initialization');
        return;
    }

    try {
        // Add navigation event listeners
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.getAttribute('href').replace('#', '');
                
                // Update active state
                document.querySelectorAll('.nav-link').forEach(navLink => {
                    navLink.classList.remove('active');
                });
                e.target.classList.add('active');
                
                // Load the selected section
                loadSection(section);
            });
        });
        
        // Load initial dashboard data
        await loadSection('dashboard');
        await loadAttendanceData();
        await loadActivities();
        await loadDeadlines();
        await loadNotices();

        console.log('Dashboard initialization complete');
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        showAlert('Error', 'Failed to load dashboard content. Please refresh the page.');
    }
});

// Function to setup section event listeners
function setupSectionEventListeners(section) {
    switch (section) {
        case 'courses':
            setupCoursesListeners();
            break;
        case 'attendance':
            setupAttendanceListeners();
            break;
        case 'assignments':
            setupAssignmentsListeners();
            break;
        case 'grades':
            setupGradesListeners();
            break;
    }
}

// Setup courses listeners
function setupCoursesListeners() {
    // Add any specific event listeners for the courses section
    const refreshButton = document.getElementById('refreshCourses');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            loadSection('courses');
            showAlert('Success', 'Course data refreshed');
        });
    }
}

// Setup attendance listeners
function setupAttendanceListeners() {
    const refreshButton = document.getElementById('refreshAttendance');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshAttendance);
    }
}

// Setup assignments listeners
function setupAssignmentsListeners() {
    const refreshButton = document.getElementById('refreshAssignments');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            loadSection('assignments');
            showAlert('Success', 'Assignments refreshed');
        });
    }
}

// Setup grades listeners
function setupGradesListeners() {
    const refreshButton = document.getElementById('refreshGrades');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            loadSection('grades');
            showAlert('Success', 'Grades refreshed');
        });
    }
}

// Function to view detailed attendance records
function viewAttendanceDetails(courseId) {
    const course = JSON.parse(localStorage.getItem(`courses_${userData.email}`))
        .find(c => c.id === courseId);
    const attendance = getAttendanceForCourse(courseId);
    const currentFaculty = JSON.parse(localStorage.getItem('currentFaculty') || '{}');
    
    const modalHtml = `
        <div class="modal fade" id="attendanceDetailsModal">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Attendance Details - ${course.code}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6>Course Information</h6>
                                <p><strong>Course:</strong> ${course.name}</p>
                                <p><strong>Faculty:</strong> ${currentFaculty.name}</p>
                                <p><strong>Faculty Email:</strong> ${currentFaculty.email}</p>
                                <p><strong>Overall Attendance:</strong> ${attendance.percentage}%</p>
                            </div>
                        </div>
                        
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Status</th>
                                        <th>Marked By</th>
                                        <th>Faculty Email</th>
                                        <th>Marked On</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${attendance.records.length > 0 ? 
                                        attendance.records.map(record => `
                                            <tr>
                                                <td>${record.date.toLocaleDateString()}</td>
                                                <td>
                                                    <span class="badge bg-${record.present ? 'success' : 'danger'}">
                                                        ${record.present ? 'Present' : 'Absent'}
                                                    </span>
                                                </td>
                                                <td>${record.markedByName}</td>
                                                <td>${record.markedByEmail}</td>
                                                <td>${record.markedAt.toLocaleString()}</td>
                                            </tr>
                                        `).join('') : 
                                        `<tr>
                                            <td colspan="5" class="text-center">
                                                <p class="text-muted">No attendance records found</p>
                                            </td>
                                        </tr>`
                                    }
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('attendanceDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add new modal to the document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('attendanceDetailsModal'));
    modal.show();
} 