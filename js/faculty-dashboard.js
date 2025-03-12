// API Endpoints
const ENDPOINTS = {
    faculty: '/api/faculty',
    courses: '/api/courses',
    students: '/api/students',
    attendance: '/api/attendance',
    notices: '/api/notices',
    activities: '/api/activities'
};

// Mock Data
const mockData = {
    faculty: {
        id: "FAC123",
        name: "Dr. Sarah Johnson",
        department: "Computer Science",
        email: "sarah.johnson@college.edu",
        phone: "+1 (555) 123-4567",
        designation: "Associate Professor",
        specialization: "Artificial Intelligence",
        joinDate: "2020-01-15",
        education: [
            { degree: "Ph.D", field: "Computer Science", university: "MIT", year: 2018 },
            { degree: "M.S.", field: "Computer Science", university: "Stanford", year: 2014 }
        ],
        achievements: [
            "Best Teacher Award 2023",
            "Published 15 research papers",
            "3 Patents in AI"
        ]
    },
    courses: [
        {
            id: "CS101",
            code: "CS101",
            name: "Introduction to Programming",
            students: 45,
            attendance: 88,
            schedule: { day: "Monday", time: "10:00 AM", room: "Lab 1" },
            syllabus: [
                "Introduction to Python",
                "Control Structures",
                "Functions and Modules",
                "Object-Oriented Programming"
            ],
            assignments: [
                { title: "Basic Programming", deadline: "2024-03-20", submitted: 40 },
                { title: "OOP Concepts", deadline: "2024-04-05", submitted: 35 }
            ],
            grades: {
                assignments: 85,
                midterm: 78,
                project: 90
            }
        },
        {
            id: "CS201",
            code: "CS201",
            name: "Data Structures",
            students: 35,
            attendance: 92,
            schedule: { day: "Tuesday", time: "2:00 PM", room: "Room 202" },
            syllabus: [
                "Arrays and Linked Lists",
                "Stacks and Queues",
                "Trees and Graphs",
                "Sorting Algorithms"
            ],
            assignments: [
                { title: "Linked List Implementation", deadline: "2024-03-25", submitted: 30 },
                { title: "Binary Trees", deadline: "2024-04-10", submitted: 28 }
            ],
            grades: {
                assignments: 88,
                midterm: 82,
                project: 85
            }
        }
    ],
    students: {
        CS101: [
            { id: "ST101", name: "John Doe", attendance: 90, grades: { midterm: 85, assignments: 88 } },
            { id: "ST102", name: "Jane Smith", attendance: 95, grades: { midterm: 92, assignments: 90 } },
            { id: "ST103", name: "Mike Johnson", attendance: 85, grades: { midterm: 78, assignments: 82 } }
        ],
        CS201: [
            { id: "ST201", name: "Alice Brown", attendance: 88, grades: { midterm: 88, assignments: 85 } },
            { id: "ST202", name: "Bob Wilson", attendance: 92, grades: { midterm: 90, assignments: 92 } }
        ]
    },
    activities: [
        {
            type: "grade",
            message: "Posted grades for CS101 midterm exam",
            time: "2 hours ago",
            course: "CS101"
        },
        {
            type: "attendance",
            message: "Updated attendance for CS201",
            time: "3 hours ago",
            course: "CS201"
        },
        {
            type: "notice",
            message: "Created new assignment for CS101",
            time: "5 hours ago",
            course: "CS101"
        }
    ],
    notices: [
        {
            id: "N1",
            title: "Midterm Schedule",
            content: "Midterm examinations will begin next week. Please check the detailed schedule.",
            date: "2024-03-15",
            type: "exam",
            priority: "high",
            courses: ["CS101", "CS201"]
        },
        {
            id: "N2",
            title: "Project Submission",
            content: "Final project submissions are due by end of month.",
            date: "2024-03-10",
            type: "deadline",
            priority: "medium",
            courses: ["CS201"]
        }
    ]
};

// Cache for section content
let sectionCache = {};

// Load user data from localStorage
const userData = JSON.parse(localStorage.getItem('userData') || '{}');

// Initialize data storage
const facultyData = {
    courses: JSON.parse(localStorage.getItem('facultyCourses') || '[]'),
    students: JSON.parse(localStorage.getItem('facultyStudents') || '[]'),
    attendance: JSON.parse(localStorage.getItem('facultyAttendance') || '[]'),
    assignments: JSON.parse(localStorage.getItem('facultyAssignments') || '[]'),
    news: JSON.parse(localStorage.getItem('facultyNews') || '[]')
};

// Save data to localStorage
function saveData(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeFacultyData();
    setupNavigation();
    loadSection('dashboard');
});

// Initialize data storage
function initializeFacultyData() {
    try {
        // Initialize with mock data if no data exists
        if (!localStorage.getItem('facultyCourses')) {
            localStorage.setItem('facultyCourses', JSON.stringify(mockData.courses));
        }
        if (!localStorage.getItem('facultyStudents')) {
            localStorage.setItem('facultyStudents', JSON.stringify([]));
        }
        if (!localStorage.getItem('facultyAttendance')) {
            localStorage.setItem('facultyAttendance', JSON.stringify([]));
        }
        if (!localStorage.getItem('facultyAssignments')) {
            localStorage.setItem('facultyAssignments', JSON.stringify([]));
        }
        if (!localStorage.getItem('facultyNews')) {
            localStorage.setItem('facultyNews', JSON.stringify([]));
        }

        // Load data into facultyData object
        facultyData.courses = JSON.parse(localStorage.getItem('facultyCourses') || '[]');
        facultyData.students = JSON.parse(localStorage.getItem('facultyStudents') || '[]');
        facultyData.attendance = JSON.parse(localStorage.getItem('facultyAttendance') || '[]');
        facultyData.assignments = JSON.parse(localStorage.getItem('facultyAssignments') || '[]');
        facultyData.news = JSON.parse(localStorage.getItem('facultyNews') || '[]');

        // Check authentication
        const authToken = localStorage.getItem('authToken');
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        
        if (!authToken || !userData) {
            window.location.replace('../login.html');
            return;
        }

        // Update UI with user info
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = userData.name || 'Faculty';
        }
    } catch (error) {
        console.error('Error initializing faculty data:', error);
        showAlert('Error', 'Failed to initialize dashboard data');
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

        console.log('Loading section:', section); // Debug log
        
        let content;
        // Check cache first
        if (sectionCache[section]) {
            content = sectionCache[section];
        } else {
            // Generate content based on section
            content = generateSectionContent(section);
            sectionCache[section] = content;
        }

        // Display content
        mainContent.innerHTML = content;
        
        // Setup event listeners for the new content
        setupSectionEventListeners(section);
        
        console.log('Section loaded successfully'); // Debug log
        
    } catch (error) {
        console.error('Error loading section:', error);
        const mainContent = document.getElementById('mainContent');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="container py-4">
                    <div class="alert alert-danger">
                        Error loading content. Please try refreshing the page.
                    </div>
                </div>
            `;
        }
    }
}

// Generate section content
function generateSectionContent(section) {
    console.log('Generating content for section:', section);
    
    switch (section) {
        case 'dashboard':
            return generateDashboardContent();
        case 'courses':
            return generateCoursesContent();
        case 'students':
            return generateStudentsContent();
        case 'attendance':
            return generateAttendanceContent();
        case 'notices':
            return generateNoticesContent();
        case 'interactions':
            return generateInteractionsContent();
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

// Setup event listeners for section content
function setupSectionEventListeners(section) {
    // Common elements
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        // Remove any existing event listeners
        const newLogoutBtn = logoutBtn.cloneNode(true);
        logoutBtn.parentNode.replaceChild(newLogoutBtn, logoutBtn);
        newLogoutBtn.addEventListener('click', handleLogout);
    }

    // Section-specific elements
    switch (section) {
        case 'dashboard':
            setupDashboardListeners();
            break;
        case 'courses':
            setupCoursesListeners();
            break;
        case 'students':
            setupStudentsListeners();
            break;
        case 'attendance':
            setupAttendanceListeners();
            break;
        case 'grades':
            setupGradesListeners();
            break;
        case 'notices':
            setupNoticesListeners();
            break;
        case 'interactions':
            setupInteractionsListeners();
            break;
    }
}

// Generate content for different sections
function generateDashboardContent() {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');

    return `
        <div class="container py-4">
            <!-- Quick Stats -->
        <div class="row mb-4">
            <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Courses</h5>
                            <p class="h2 mb-0">${facultyData.courses.length}</p>
                        </div>
                </div>
            </div>
            <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Students</h5>
                            <p class="h2 mb-0">${facultyData.students.length}</p>
                        </div>
                </div>
            </div>
            <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Assignments</h5>
                            <p class="h2 mb-0">${facultyData.assignments.length}</p>
                        </div>
                </div>
            </div>
            <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>News</h5>
                            <p class="h2 mb-0">${facultyData.news.length}</p>
                        </div>
                </div>
            </div>
        </div>

            <!-- Quick Actions -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                    <div class="card-header">
                            <h5 class="mb-0">Quick Actions</h5>
                    </div>
                    <div class="card-body">
                            <div class="d-flex gap-2">
                                <button class="btn btn-primary" onclick="showAddCourseModal()">
                                    <i class="fas fa-plus"></i> Add Course
                                </button>
                                <button class="btn btn-success" onclick="showAddStudentModal()">
                                    <i class="fas fa-user-plus"></i> Add Student
                                </button>
                                <button class="btn btn-info" onclick="showAddAssignmentModal()">
                                    <i class="fas fa-tasks"></i> Add Assignment
                                </button>
                                <button class="btn btn-warning" onclick="showAddNewsModal()">
                                    <i class="fas fa-newspaper"></i> Add News
                                </button>
                                    </div>
                                </div>
                    </div>
                </div>
            </div>

            <!-- Latest News and Recent Assignments -->
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Latest News</h5>
                            <button class="btn btn-sm btn-primary" onclick="showAddNewsModal()">Add News</button>
                        </div>
                        <div class="card-body">
                            ${facultyData.news.length > 0 ? 
                                facultyData.news.slice(0, 5).map(news => `
                                    <div class="news-item mb-3">
                                        <h6>${news.title}</h6>
                                        <p>${news.content}</p>
                                        <small class="text-muted">${new Date(news.date).toLocaleDateString()}</small>
                                    </div>
                                `).join('') : 
                                '<p class="text-muted">No news available</p>'
                            }
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Recent Assignments</h5>
                            <button class="btn btn-sm btn-primary" onclick="showAddAssignmentModal()">Add Assignment</button>
                    </div>
                    <div class="card-body">
                            ${facultyData.assignments.length > 0 ? 
                                facultyData.assignments.slice(0, 5).map(assignment => `
                                    <div class="assignment-item mb-3">
                                        <h6>${assignment.title}</h6>
                                        <p>Course: ${assignment.courseId}</p>
                                        <small class="text-muted">Due: ${new Date(assignment.dueDate).toLocaleDateString()}</small>
                                </div>
                                `).join('') : 
                                '<p class="text-muted">No assignments available</p>'
                            }
                            </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateCoursesContent() {
    const courses = facultyData.courses;
    
    return `
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Course Management</h2>
                <button class="btn btn-primary" onclick="showAddCourseModal()">
                    <i class="fas fa-plus"></i> Add Course
                </button>
        </div>

            <div class="row" id="coursesList">
                ${courses.length > 0 ? courses.map(course => `
                    <div class="col-md-6 col-lg-4 mb-4">
                        <div class="card h-100">
            <div class="card-body">
                                <h5 class="card-title">${course.name}</h5>
                                <h6 class="card-subtitle mb-2 text-muted">${course.code}</h6>
                                <p class="card-text">${course.description || 'No description available'}</p>
                                <p class="card-text">
                                    <small class="text-muted">
                                        <i class="fas fa-users"></i> ${course.students?.length || 0} Students
                                    </small>
                                </p>
                                            </div>
                            <div class="card-footer bg-transparent border-top-0">
                                <button class="btn btn-sm btn-outline-primary me-2" onclick="viewCourse('${course.id}')">
                                    <i class="fas fa-eye"></i> View
                                        </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="editCourse('${course.id}')">
                                    <i class="fas fa-edit"></i> Edit
                                        </button>
                            </div>
                        </div>
                    </div>
                `).join('') : `
                    <div class="col-12">
                        <div class="alert alert-info">
                            No courses added yet. Click the "Add Course" button to add your first course.
                        </div>
                    </div>
                `}
            </div>
        </div>

        <!-- Add Course Modal -->
        <div class="modal fade" id="addCourseModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Course</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addCourseForm">
                            <div class="mb-3">
                                <label for="courseCode" class="form-label">Course Code</label>
                                <input type="text" class="form-control" id="courseCode" required>
                            </div>
                            <div class="mb-3">
                                <label for="courseName" class="form-label">Course Name</label>
                                <input type="text" class="form-control" id="courseName" required>
                            </div>
                            <div class="mb-3">
                                <label for="courseDescription" class="form-label">Description</label>
                                <textarea class="form-control" id="courseDescription" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <label for="courseSchedule" class="form-label">Schedule</label>
                                <input type="text" class="form-control" id="courseSchedule" placeholder="e.g., Monday 10:00 AM">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="addCourse()">Add Course</button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showAddCourseModal() {
    // Create modal HTML
    const modalHtml = `
        <div class="modal fade" id="addCourseModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Course</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addCourseForm">
                            <div class="mb-3">
                                <label for="courseCode" class="form-label">Course Code</label>
                                <input type="text" class="form-control" id="courseCode" required>
                            </div>
                            <div class="mb-3">
                                <label for="courseName" class="form-label">Course Name</label>
                                <input type="text" class="form-control" id="courseName" required>
                            </div>
                            <div class="mb-3">
                                <label for="courseDescription" class="form-label">Description</label>
                                <textarea class="form-control" id="courseDescription" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <label for="courseSchedule" class="form-label">Schedule</label>
                                <input type="text" class="form-control" id="courseSchedule" placeholder="e.g., Monday 10:00 AM">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="addCourse()">Add Course</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('addCourseModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Initialize and show the modal
    const modal = new bootstrap.Modal(document.getElementById('addCourseModal'));
    modal.show();

    // Add event listener for form submission
    const form = document.getElementById('addCourseForm');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        addCourse();
    });

    // Cleanup on modal close
    document.getElementById('addCourseModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function addCourse() {
    try {
        // Get form values
        const code = document.getElementById('courseCode').value;
        const name = document.getElementById('courseName').value;
        const description = document.getElementById('courseDescription').value;
        const schedule = document.getElementById('courseSchedule').value;

        // Validate required fields
        if (!code || !name) {
            showAlert('Error', 'Course code and name are required');
            return;
        }

        // Check if course code already exists
        if (facultyData.courses.some(course => course.code === code)) {
            showAlert('Error', 'A course with this code already exists');
            return;
        }

        // Create new course object
        const newCourse = {
            id: 'C' + Date.now(),
            code: code,
            name: name,
            description: description,
            schedule: schedule,
            students: [],
            attendance: [],
            assignments: [],
            grades: {},
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        // Add to courses array
        facultyData.courses.push(newCourse);

        // Save to localStorage
        saveData('facultyCourses', facultyData.courses);

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addCourseModal'));
        modal.hide();

        // Clear form
        document.getElementById('addCourseForm').reset();

        // Show success message
        showAlert('Success', 'Course added successfully');

        // Refresh courses section
        loadSection('courses');

    } catch (error) {
        console.error('Error adding course:', error);
        showAlert('Error', 'Failed to add course. Please try again.');
    }
}

function setupCoursesListeners() {
    // Add event listeners for course-related actions
    const addCourseForm = document.getElementById('addCourseForm');
    if (addCourseForm) {
        addCourseForm.addEventListener('submit', (e) => {
            e.preventDefault();
            addCourse();
        });
    }
}

// Event listener setup functions
function setupDashboardListeners() {
    // Add dashboard-specific event listeners
}

function setupNoticesListeners() {
    const createNoticeBtn = document.getElementById('createNoticeBtn');
    if (createNoticeBtn) {
        createNoticeBtn.addEventListener('click', handleCreateNotice);
    }

    // Add event listeners for edit and delete buttons
    document.querySelectorAll('[data-notice-id]').forEach(btn => {
        if (btn.classList.contains('btn-primary')) {
            btn.addEventListener('click', () => editNotice(btn.dataset.noticeId));
        } else if (btn.classList.contains('btn-danger')) {
            btn.addEventListener('click', () => deleteNotice(btn.dataset.noticeId));
        }
    });
}

// Utility functions
function getActivityIcon(type) {
    const icons = {
        grade: 'chart-bar',
        attendance: 'check-square',
        notice: 'bell',
        course: 'book'
    };
    return icons[type] || 'info-circle';
}

function getPriorityClass(priority) {
    const classes = {
        high: 'danger',
        medium: 'warning',
        low: 'info'
    };
    return classes[priority] || 'secondary';
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function showAlert(title, message) {
    const alertModal = new bootstrap.Modal(document.getElementById('alertModal'));
    document.getElementById('alertModalTitle').textContent = title;
    document.getElementById('alertModalBody').textContent = message;
    alertModal.show();
}

// Handler functions
function handleLogout(e) {
    if (e) {
    e.preventDefault();
    }
    
    try {
        // Clear all stored data
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        localStorage.removeItem('facultyCourses');
        localStorage.removeItem('facultyStudents');
        localStorage.removeItem('facultyAttendance');
        localStorage.removeItem('facultyAssignments');
        localStorage.removeItem('facultyNews');
    sessionStorage.clear();
    
        // Clear section cache
        sectionCache = {};
        
        // Force redirect to login page
        window.location.replace('../login.html');
    } catch (error) {
        console.error('Error during logout:', error);
        alert('Failed to logout. Please try again.');
    }
}

function handleAddCourse(e) {
    e.preventDefault();
    
    const modalHtml = `
        <div class="modal fade" id="addCourseModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Course</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addCourseForm">
                            <div class="mb-3">
                                <label class="form-label">Course Code</label>
                                <input type="text" class="form-control" name="courseCode" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Course Name</label>
                                <input type="text" class="form-control" name="courseName" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" name="description" rows="3" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Schedule</label>
                                <div class="row">
                                    <div class="col">
                                        <select class="form-select" name="day" required>
                                            <option value="">Select Day</option>
                                            <option value="Monday">Monday</option>
                                            <option value="Tuesday">Tuesday</option>
                                            <option value="Wednesday">Wednesday</option>
                                            <option value="Thursday">Thursday</option>
                                            <option value="Friday">Friday</option>
                                        </select>
                                    </div>
                                    <div class="col">
                                        <input type="time" class="form-control" name="time" required>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="addCourse()">Add Course</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Initialize modal
    const modal = new bootstrap.Modal(document.getElementById('addCourseModal'));
    modal.show();
}

function handleCreateNotice(e) {
    e.preventDefault();
    
    const modalHtml = `
        <div class="modal fade" id="createNoticeModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Create New Notice</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="createNoticeForm">
                            <div class="mb-3">
                                <label class="form-label">Title</label>
                                <input type="text" class="form-control" name="title" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Content</label>
                                <textarea class="form-control" name="content" rows="4" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Type</label>
                                <select class="form-select" name="type" required>
                                    <option value="">Select Type</option>
                                    <option value="exam">Exam</option>
                                    <option value="deadline">Deadline</option>
                                    <option value="announcement">Announcement</option>
                                    <option value="event">Event</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Priority</label>
                                <select class="form-select" name="priority" required>
                                    <option value="">Select Priority</option>
                                    <option value="high">High</option>
                                    <option value="medium">Medium</option>
                                    <option value="low">Low</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Target Courses</label>
                                <div class="course-checkboxes">
                                    ${facultyData.courses.map(course => `
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" 
                                                name="courses" value="${course.code}" id="course${course.code}">
                                            <label class="form-check-label" for="course${course.code}">
                                                ${course.code} - ${course.name}
                                            </label>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveNoticeBtn">Create Notice</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Initialize modal
    const modal = new bootstrap.Modal(document.getElementById('createNoticeModal'));
    modal.show();

    // Setup event listeners
    const form = document.getElementById('createNoticeForm');
    const saveBtn = document.getElementById('saveNoticeBtn');

    // Save notice
    saveBtn.addEventListener('click', () => {
        if (form.checkValidity()) {
            const formData = new FormData(form);
            const newNotice = {
                id: 'N' + (mockData.notices.length + 1),
                title: formData.get('title'),
                content: formData.get('content'),
                type: formData.get('type'),
                priority: formData.get('priority'),
                date: new Date().toISOString().split('T')[0],
                courses: Array.from(formData.getAll('courses'))
            };

            // Add to mock data
            mockData.notices.push(newNotice);

            // Add to activities
            mockData.activities.unshift({
                type: 'notice',
                message: `Created new notice: ${newNotice.title}`,
                time: 'Just now',
                course: newNotice.courses[0]
            });

            // Close modal and refresh
            modal.hide();
            document.getElementById('createNoticeModal').remove();
            loadSection('notices');
            showAlert('Notice created successfully', 'success');
        } else {
            form.reportValidity();
        }
    });

    // Cleanup on modal close
    document.getElementById('createNoticeModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function editNotice(noticeId) {
    const notice = mockData.notices.find(n => n.id === noticeId);
    if (!notice) return;

    const modalHtml = `
        <div class="modal fade" id="editNoticeModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Notice</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editNoticeForm">
                            <div class="mb-3">
                                <label class="form-label">Title</label>
                                <input type="text" class="form-control" name="title" value="${notice.title}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Content</label>
                                <textarea class="form-control" name="content" rows="4" required>${notice.content}</textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Type</label>
                                <select class="form-select" name="type" required>
                                    ${['exam', 'deadline', 'announcement', 'event'].map(type => `
                                        <option value="${type}" ${notice.type === type ? 'selected' : ''}>
                                            ${type.charAt(0).toUpperCase() + type.slice(1)}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Priority</label>
                                <select class="form-select" name="priority" required>
                                    ${['high', 'medium', 'low'].map(priority => `
                                        <option value="${priority}" ${notice.priority === priority ? 'selected' : ''}>
                                            ${priority.charAt(0).toUpperCase() + priority.slice(1)}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Target Courses</label>
                                <div class="course-checkboxes">
                                    ${facultyData.courses.map(course => `
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" 
                                                name="courses" value="${course.code}" 
                                                id="course${course.code}"
                                                ${notice.courses.includes(course.code) ? 'checked' : ''}>
                                            <label class="form-check-label" for="course${course.code}">
                                                ${course.code} - ${course.name}
                                            </label>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="updateNoticeBtn">Update Notice</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Initialize modal
    const modal = new bootstrap.Modal(document.getElementById('editNoticeModal'));
    modal.show();

    // Setup event listeners
    const form = document.getElementById('editNoticeForm');
    const updateBtn = document.getElementById('updateNoticeBtn');

    // Update notice
    updateBtn.addEventListener('click', () => {
        if (form.checkValidity()) {
            const formData = new FormData(form);
            
            // Update notice data
            notice.title = formData.get('title');
            notice.content = formData.get('content');
            notice.type = formData.get('type');
            notice.priority = formData.get('priority');
            notice.courses = Array.from(formData.getAll('courses'));

            // Add to activities
            mockData.activities.unshift({
                type: 'notice',
                message: `Updated notice: ${notice.title}`,
                time: 'Just now',
                course: notice.courses[0]
            });

            // Close modal and refresh
            modal.hide();
            document.getElementById('editNoticeModal').remove();
            loadSection('notices');
            showAlert('Notice updated successfully', 'success');
        } else {
            form.reportValidity();
        }
    });

    // Cleanup on modal close
    document.getElementById('editNoticeModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function deleteNotice(noticeId) {
    const notice = mockData.notices.find(n => n.id === noticeId);
    if (!notice) return;

    if (confirm(`Are you sure you want to delete the notice "${notice.title}"?`)) {
        // Remove notice from mock data
        const index = mockData.notices.findIndex(n => n.id === noticeId);
        if (index > -1) {
            mockData.notices.splice(index, 1);
        }

        // Add to activities
        mockData.activities.unshift({
            type: 'notice',
            message: `Deleted notice: ${notice.title}`,
            time: 'Just now',
            course: notice.courses[0]
        });

        // Refresh notices section
        loadSection('notices');
        showAlert('Notice deleted successfully', 'success');
    }
}

function generateStudentsContent() {
    return `
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Student Management</h2>
                <button class="btn btn-primary" onclick="showAddStudentModal()">
                    <i class="fas fa-user-plus"></i> Add Student
                </button>
        </div>

            ${facultyData.courses.map(course => `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">${course.code} - ${course.name}</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Student ID</th>
                                        <th>Name</th>
                                        <th>Attendance</th>
                                        <th>Midterm</th>
                                        <th>Assignments</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(facultyData.students.filter(student => student.courseId === course.id) || []).map(student => `
                                        <tr>
                                            <td>${student.rollNumber}</td>
                                            <td>${student.name}</td>
                                            <td>
                                                <div class="progress">
                                                    <div class="progress-bar ${student.attendance >= 75 ? 'bg-success' : 'bg-warning'}" 
                                                        role="progressbar" 
                                                        style="width: ${student.attendance || 0}%">
                                                        ${student.attendance || 0}%
                                                    </div>
                                                </div>
                                            </td>
                                            <td>${student.grades?.midterm || 'N/A'}</td>
                                            <td>${student.grades?.assignments || 'N/A'}</td>
                                            <td>
                                                <button class="btn btn-sm btn-primary me-1" onclick="editStudent('${student.id}')">
                                                    <i class="fas fa-edit"></i>
                                                </button>
                                                <button class="btn btn-sm btn-danger" onclick="deleteStudent('${student.id}')">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `).join('')}
                </div>
            `;
}

function showAddStudentModal() {
    const modalHtml = `
        <div class="modal fade" id="addStudentModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Student</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addStudentForm">
                            <div class="mb-3">
                                <label class="form-label">Student ID/Roll Number</label>
                                <input type="text" class="form-control" name="rollNumber" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Full Name</label>
                                <input type="text" class="form-control" name="studentName" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Course</label>
                                <select class="form-select" name="courseId" required>
                                    <option value="">Select Course</option>
                                    ${facultyData.courses.map(course => `
                                        <option value="${course.id}">${course.code} - ${course.name}</option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" name="email" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Initial Attendance (%)</label>
                                <input type="number" class="form-control" name="attendance" min="0" max="100" value="0">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Initial Grades</label>
                                <div class="row">
                                    <div class="col-md-6">
                                        <label class="form-label">Midterm</label>
                                        <input type="number" class="form-control" name="midterm" min="0" max="100">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Assignments</label>
                                        <input type="number" class="form-control" name="assignments" min="0" max="100">
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="addStudent()">Add Student</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('addStudentModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Initialize and show modal
    const modal = new bootstrap.Modal(document.getElementById('addStudentModal'));
    modal.show();
}

// Add this after the mock data section

// Function to verify if student email is registered
async function verifyStudentEmail(email) {
    // In a real app, this would be an API call
    // For now, we'll check localStorage
    const registeredStudents = JSON.parse(localStorage.getItem('registeredStudents') || '[]');
    return registeredStudents.includes(email);
}

// Function to show error modal
function showErrorModal(title, message) {
    const modalHtml = `
        <div class="modal fade" id="errorModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('errorModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('errorModal'));
    modal.show();
}

// Modify the addStudent function
async function addStudent() {
    const form = document.getElementById('addStudentForm');
    if (form.checkValidity()) {
        const formData = new FormData(form);
        const studentEmail = formData.get('email');
        
        // Verify student email
        const isRegistered = await verifyStudentEmail(studentEmail);
        if (!isRegistered) {
            showErrorModal('Invalid Student Email', 
                'This email is not registered in the system. Only registered students can be added to courses.');
            return;
        }

        // Check if student ID already exists
        if (facultyData.students.some(s => s.rollNumber === formData.get('rollNumber'))) {
            showAlert('Error', 'A student with this ID already exists');
            return;
        }

        const student = {
            id: 'S' + Date.now(),
            rollNumber: formData.get('rollNumber'),
            name: formData.get('studentName'),
            courseId: formData.get('courseId'),
            email: studentEmail,
            attendance: parseInt(formData.get('attendance')) || 0,
            grades: {
                midterm: parseInt(formData.get('midterm')) || 0,
                assignments: parseInt(formData.get('assignments')) || 0
            },
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        // Add to students array
        facultyData.students.push(student);

        // Save to localStorage
        saveData('facultyStudents', facultyData.students);

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addStudentModal'));
        modal.hide();

        // Show success message
        showAlert('Success', 'Student added successfully');

        // Refresh students section
        loadSection('students');
    } else {
        form.reportValidity();
    }
}

function editStudent(studentId) {
    const student = facultyData.students.find(s => s.id === studentId);
    if (!student) return;

    const modalHtml = `
        <div class="modal fade" id="editStudentModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Student</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editStudentForm">
                            <div class="mb-3">
                                <label class="form-label">Student ID/Roll Number</label>
                                <input type="text" class="form-control" name="rollNumber" value="${student.rollNumber}" readonly>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Full Name</label>
                                <input type="text" class="form-control" name="studentName" value="${student.name}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Course</label>
                                <select class="form-select" name="courseId" required>
                                    ${facultyData.courses.map(course => `
                                        <option value="${course.id}" ${course.id === student.courseId ? 'selected' : ''}>
                                            ${course.code} - ${course.name}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" name="email" value="${student.email}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Attendance (%)</label>
                                <input type="number" class="form-control" name="attendance" 
                                    min="0" max="100" value="${student.attendance || 0}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Grades</label>
                                <div class="row">
                                    <div class="col-md-6">
                                        <label class="form-label">Midterm</label>
                                        <input type="number" class="form-control" name="midterm" 
                                            min="0" max="100" value="${student.grades?.midterm || 0}">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Assignments</label>
                                        <input type="number" class="form-control" name="assignments" 
                                            min="0" max="100" value="${student.grades?.assignments || 0}">
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="updateStudent('${student.id}')">Update Student</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('editStudentModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Initialize and show modal
    const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
    modal.show();
}

function updateStudent(studentId) {
    const form = document.getElementById('editStudentForm');
    if (form.checkValidity()) {
        const formData = new FormData(form);
        const studentIndex = facultyData.students.findIndex(s => s.id === studentId);
        
        if (studentIndex === -1) {
            showAlert('Error', 'Student not found');
            return;
        }

        // Update student data
        facultyData.students[studentIndex] = {
            ...facultyData.students[studentIndex],
            name: formData.get('studentName'),
            courseId: formData.get('courseId'),
            email: formData.get('email'),
            attendance: parseInt(formData.get('attendance')) || 0,
            grades: {
                midterm: parseInt(formData.get('midterm')) || 0,
                assignments: parseInt(formData.get('assignments')) || 0
            },
            updatedAt: new Date().toISOString()
        };

        // Save to localStorage
        saveData('facultyStudents', facultyData.students);

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editStudentModal'));
        modal.hide();

        // Show success message
        showAlert('Success', 'Student information updated successfully');

        // Refresh students section
        loadSection('students');
    } else {
        form.reportValidity();
    }
}

function deleteStudent(studentId) {
    const student = facultyData.students.find(s => s.id === studentId);
    if (!student) return;

    if (confirm(`Are you sure you want to delete student ${student.name} (${student.rollNumber})?`)) {
        // Remove student from array
        facultyData.students = facultyData.students.filter(s => s.id !== studentId);

        // Save to localStorage
        saveData('facultyStudents', facultyData.students);

        // Show success message
        showAlert('Success', 'Student deleted successfully');

        // Refresh students section
        loadSection('students');
    }
}

function setupStudentsListeners() {
    // Add event listeners for student-related actions
    const addStudentForm = document.getElementById('addStudentForm');
    if (addStudentForm) {
        addStudentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            addStudent();
        });
    }
}

function generateAttendanceContent() {
    return `
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Attendance Management</h2>
        </div>

            ${facultyData.courses.map(course => {
                const courseStudents = facultyData.students.filter(s => s.courseId === course.id);
                const maxAttendanceCount = Math.max(...courseStudents.map(student => 
                    (student.attendanceRecord || []).filter(record => record.present).length
                ));
                
                return `
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">${course.code} - ${course.name}</h5>
                            <button class="btn btn-primary" onclick="handleMarkAttendance('${course.id}')">
                                <i class="fas fa-user-check"></i> Mark Attendance
                                </button>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Student ID</th>
                                            <th>Name</th>
                                            <th>Email</th>
                                            <th>Present Count</th>
                                            <th>Present Today</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${courseStudents.map(student => {
                                            const presentCount = (student.attendanceRecord || []).filter(record => record.present).length;
                                            const attendancePercentage = maxAttendanceCount > 0 ? 
                                                Math.round((presentCount / maxAttendanceCount) * 100) : 100;
                                            
                                            return `
                                                <tr>
                                                    <td>${student.rollNumber}</td>
                                                    <td>${student.name}</td>
                                                    <td>${student.email}</td>
                                                    <td>${presentCount} / ${maxAttendanceCount}</td>
                                                    <td>
                                                        <div class="progress">
                                                            <div class="progress-bar ${attendancePercentage >= 75 ? 'bg-success' : 'bg-warning'}" 
                                                                role="progressbar" 
                                                                style="width: ${attendancePercentage}%" 
                                                                aria-valuenow="${attendancePercentage}" 
                                        aria-valuemin="0" 
                                        aria-valuemax="100">
                                                                ${attendancePercentage}%
                                    </div>
                                </div>
                                                    </td>
                                                    <td>
                                                        <span class="badge ${attendancePercentage >= 75 ? 'bg-success' : 'bg-warning'}">
                                                            ${attendancePercentage === 100 ? 'Highest' : 
                                                              attendancePercentage >= 75 ? 'Regular' : 'Irregular'}
                                            </span>
                                                    </td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                                        </div>
                                    </div>
                            </div>
                `;
            }).join('')}
                        </div>
    `;
}

// Add this after the mock data section

// Function to verify if student email is registered
async function verifyStudentEmail(email) {
    // In a real app, this would be an API call
    // For now, we'll check localStorage
    const registeredStudents = JSON.parse(localStorage.getItem('registeredStudents') || '[]');
    return registeredStudents.includes(email);
}

// Function to show error modal
function showErrorModal(title, message) {
    const modalHtml = `
        <div class="modal fade" id="errorModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('errorModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('errorModal'));
    modal.show();
}

// Modify the handleMarkAttendance function
async function handleMarkAttendance(courseId) {
    const course = facultyData.courses.find(c => c.id === courseId);
    if (!course) {
        showAlert('Error', 'Course not found');
        return;
    }

    const students = facultyData.students.filter(s => s.courseId === courseId);
    
    // Verify all student emails before proceeding
    for (const student of students) {
        const isRegistered = await verifyStudentEmail(student.email);
        if (!isRegistered) {
            showErrorModal('Invalid Student Email', 
                `Student ${student.name} (${student.email}) is not registered in the system. Please remove this student and add them again with a valid email.`);
            return;
        }
    }

    const today = new Date().toISOString().split('T')[0];

    // Create modal HTML
    const modalHtml = `
        <div class="modal fade" id="markAttendanceModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Mark Attendance: ${course.code} - ${course.name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="markAttendanceForm">
                            <div class="mb-3">
                                <label class="form-label">Date</label>
                                <input type="date" class="form-control" name="attendanceDate" value="${today}" required>
                            </div>
                            <div class="mb-3">
                                <div class="d-flex justify-content-end gap-2 mb-2">
                                    <button type="button" class="btn btn-secondary" id="markAllBtn">Mark All Present</button>
                                    <button type="button" class="btn btn-secondary" id="unmarkAllBtn">Mark All Absent</button>
                                </div>
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Student ID</th>
                                                <th>Name</th>
                                                <th>Email</th>
                                                <th>Present Count</th>
                                                <th>Present Today</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${students.map(student => `
                                                <tr>
                                                    <td>${student.rollNumber}</td>
                                                    <td>${student.name}</td>
                                                    <td>${student.email}</td>
                                                    <td>${(student.attendanceRecord || []).filter(record => record.present).length}</td>
                                                    <td>
                                                        <div class="form-check">
                                                            <input class="form-check-input attendance-checkbox" 
                                                                type="checkbox" 
                                                                name="attendance" 
                                                                value="${student.id}"
                                                                data-email="${student.email}"
                                                                checked>
                                                        </div>
                                                    </td>
                                                </tr>
            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveAttendanceBtn">Save Attendance</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('markAttendanceModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Initialize modal
    const modal = new bootstrap.Modal(document.getElementById('markAttendanceModal'));
    modal.show();

    // Setup event listeners
    const form = document.getElementById('markAttendanceForm');
    const markAllBtn = document.getElementById('markAllBtn');
    const unmarkAllBtn = document.getElementById('unmarkAllBtn');
    const saveAttendanceBtn = document.getElementById('saveAttendanceBtn');

    // Mark all present
    markAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.attendance-checkbox').forEach(checkbox => {
            checkbox.checked = true;
        });
    });

    // Mark all absent
    unmarkAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.attendance-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
    });

    // Save attendance
    saveAttendanceBtn.addEventListener('click', async () => {
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const attendanceDate = formData.get('attendanceDate');
        const presentStudentIds = formData.getAll('attendance');

        // Update attendance records for each student
        for (const student of students) {
            const wasPresent = presentStudentIds.includes(student.id);
            
            // Initialize attendance record if it doesn't exist
            if (!student.attendanceRecord) {
                student.attendanceRecord = [];
            }

            // Add new attendance record
            const attendanceRecord = {
                date: attendanceDate,
                present: wasPresent,
                courseId: courseId,
                courseName: course.name,
                courseCode: course.code,
                markedBy: userData.full_name,
                markedAt: new Date().toISOString(),
                studentEmail: student.email
            };

            student.attendanceRecord.push(attendanceRecord);

            // Store attendance in localStorage with email reference
            const attendanceKey = `attendance_${student.email}_${courseId}`;
            const existingAttendance = JSON.parse(localStorage.getItem(attendanceKey) || '[]');
            existingAttendance.push(attendanceRecord);
            localStorage.setItem(attendanceKey, JSON.stringify(existingAttendance));
        }

        // Calculate attendance percentages
        const maxAttendanceCount = Math.max(...students.map(student => 
            (student.attendanceRecord || []).filter(record => record.present).length
        ));

        // Update attendance percentages
        students.forEach(student => {
            const presentCount = (student.attendanceRecord || []).filter(record => record.present).length;
            student.attendance = maxAttendanceCount > 0 ? 
                Math.round((presentCount / maxAttendanceCount) * 100) : 100;
            student.presentCount = presentCount;
        });

        // Save updated student data
        saveData('facultyStudents', facultyData.students);

        // Close modal
        modal.hide();

        // Show success message
        showAlert('Success', 'Attendance marked successfully');

        // Refresh attendance section
        loadSection('attendance');
    });

    // Cleanup on modal close
    document.getElementById('markAttendanceModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function generateGradesContent() {
    return `
        <div class="faculty-dashboard-header">
            <div class="d-flex justify-content-between align-items-center">
                <h2>Grade Management</h2>
            </div>
        </div>

        ${facultyData.courses.map(course => `
            <div class="faculty-card mb-4">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">${course.code} - ${course.name}</h5>
                        <button class="faculty-action-btn" data-course-id="${course.id}">
                            <i class="fas fa-plus"></i> Add Grades
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="grade-summary mb-4">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="grade-stat">
                                    <h6>Assignments</h6>
                                    <h3>${course.grades.assignments}%</h3>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="grade-stat">
                                    <h6>Midterm</h6>
                                    <h3>${course.grades.midterm}%</h3>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="grade-stat">
                                    <h6>Project</h6>
                                    <h3>${course.grades.project}%</h3>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Student</th>
                                    <th>Assignments</th>
                                    <th>Midterm</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${facultyData.students[course.code]?.map(student => `
                                    <tr>
                                        <td>${student.name}</td>
                                        <td>${student.grades.assignments}</td>
                                        <td>${student.grades.midterm}</td>
                                        <td>
                                            <button class="btn btn-sm btn-primary me-1" data-student-id="${student.id}">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                        </td>
                                    </tr>
                                `).join('') || ''}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `).join('')}
    `;
}

function generateNoticesContent() {
    return `
        <div class="faculty-dashboard-header">
            <div class="d-flex justify-content-between align-items-center">
                <h2>Notice Management</h2>
                <button class="faculty-action-btn" id="createNoticeBtn">
                    <i class="fas fa-plus"></i> New Notice
                </button>
            </div>
        </div>

        <div class="row">
            <div class="col-md-8">
                <div class="faculty-card">
                    <div class="card-header">
                        <h5 class="mb-0">All Notices</h5>
                    </div>
                    <div class="card-body">
                        ${mockData.notices.map(notice => `
                            <div class="notice-item mb-4">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h5 class="mb-0">${notice.title}</h5>
                                    <span class="badge bg-${getPriorityClass(notice.priority)}">${notice.priority}</span>
                                </div>
                                <p>${notice.content}</p>
                                <div class="notice-meta">
                                    <small class="text-muted me-3">
                                        <i class="fas fa-calendar me-1"></i> ${formatDate(notice.date)}
                                    </small>
                                    <small class="text-muted me-3">
                                        <i class="fas fa-tag me-1"></i> ${notice.type}
                                    </small>
                                    <small class="text-muted">
                                        <i class="fas fa-users me-1"></i> 
                                        ${notice.courses.map(code => mockData.courses.find(c => c.code === code)?.name).join(', ')}
                                    </small>
                                </div>
                                <div class="notice-actions mt-2">
                                    <button class="btn btn-sm btn-primary me-1" data-notice-id="${notice.id}">
                                        <i class="fas fa-edit"></i> Edit
                                    </button>
                                    <button class="btn btn-sm btn-danger" data-notice-id="${notice.id}">
                                        <i class="fas fa-trash"></i> Delete
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="faculty-card">
                    <div class="card-header">
                        <h5 class="mb-0">Notice Statistics</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <h6>By Priority</h6>
                            <div class="notice-stat">
                                <span>High Priority</span>
                                <span class="badge bg-danger">${mockData.notices.filter(n => n.priority === 'high').length}</span>
                            </div>
                            <div class="notice-stat">
                                <span>Medium Priority</span>
                                <span class="badge bg-warning">${mockData.notices.filter(n => n.priority === 'medium').length}</span>
                            </div>
                        </div>
                        <div>
                            <h6>By Type</h6>
                            <div class="notice-stat">
                                <span>Exam</span>
                                <span class="badge bg-info">${mockData.notices.filter(n => n.type === 'exam').length}</span>
                            </div>
                            <div class="notice-stat">
                                <span>Deadline</span>
                                <span class="badge bg-primary">${mockData.notices.filter(n => n.type === 'deadline').length}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Add new event listener setup functions
function setupStudentsListeners() {
    document.querySelectorAll('[data-student-id]').forEach(btn => {
        btn.addEventListener('click', (e) => handleEditStudent(e.target.dataset.studentId));
    });
}

function setupAttendanceListeners() {
    document.querySelectorAll('[data-course-id]').forEach(btn => {
        btn.addEventListener('click', (e) => handleMarkAttendance(e.target.dataset.courseId));
    });
}

function setupGradesListeners() {
    document.querySelectorAll('[data-course-id]').forEach(btn => {
        btn.addEventListener('click', (e) => handleAddGrades(e.target.dataset.courseId));
    });
}

// Add new handler functions
function handleEditStudent(studentId) {
    const courseCode = Object.keys(mockData.students).find(code => 
        mockData.students[code].some(s => s.id === studentId)
    );
    
    if (!courseCode) return;
    
    const student = mockData.students[courseCode].find(s => s.id === studentId);
    const course = mockData.courses.find(c => c.code === courseCode);

    const modalHtml = `
        <div class="modal fade" id="editStudentModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Student: ${student.name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editStudentForm">
                            <div class="mb-3">
                                <label class="form-label">Student Name</label>
                                <input type="text" class="form-control" name="name" value="${student.name}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Attendance (%)</label>
                                <input type="number" class="form-control" name="attendance" 
                                    value="${student.attendance}" min="0" max="100" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Midterm Grade</label>
                                <input type="number" class="form-control" name="midterm" 
                                    value="${student.grades.midterm}" min="0" max="100" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Assignments Grade</label>
                                <input type="number" class="form-control" name="assignments" 
                                    value="${student.grades.assignments}" min="0" max="100" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="updateStudentBtn">Update Student</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Initialize modal
    const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
    modal.show();

    // Setup event listeners
    const form = document.getElementById('editStudentForm');
    const updateBtn = document.getElementById('updateStudentBtn');

    // Update student
    updateBtn.addEventListener('click', () => {
        if (form.checkValidity()) {
            const formData = new FormData(form);
            
            // Update student data
            student.name = formData.get('name');
            student.attendance = parseInt(formData.get('attendance'));
            student.grades.midterm = parseInt(formData.get('midterm'));
            student.grades.assignments = parseInt(formData.get('assignments'));

            // Update course average attendance
            const courseStudents = mockData.students[courseCode];
            course.attendance = Math.round(
                courseStudents.reduce((sum, s) => sum + s.attendance, 0) / courseStudents.length
            );

            // Add to activities
            mockData.activities.unshift({
                type: 'grade',
                message: `Updated grades for student ${student.name} in ${courseCode}`,
                time: 'Just now',
                course: courseCode
            });

            // Close modal and refresh
            modal.hide();
            document.getElementById('editStudentModal').remove();
            loadSection('students');
            showAlert('Student information updated successfully', 'success');
        } else {
            form.reportValidity();
        }
    });

    // Cleanup on modal close
    document.getElementById('editStudentModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function handleAddGrades(courseId) {
    // Implement grade addition functionality
    showAlert('Grade addition feature coming soon', 'info');
}

function viewCourse(courseId) {
    const course = mockData.courses.find(c => c.id === courseId);
    if (!course) return;

    const modalHtml = `
        <div class="modal fade" id="viewCourseModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${course.code} - ${course.name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <h6>Schedule</h6>
                                <p>${course.schedule.day} at ${course.schedule.time}</p>
                                <p>Room: ${course.schedule.room}</p>
                            </div>
                            <div class="col-md-6">
                                <h6>Statistics</h6>
                                <p>Total Students: ${course.students}</p>
                                <p>Average Attendance: ${course.attendance}%</p>
                            </div>
                        </div>
                        <div class="mb-4">
                            <h6>Syllabus</h6>
                            <ul class="list-group">
                                ${course.syllabus.map(topic => `
                                    <li class="list-group-item">${topic}</li>
                                `).join('')}
                            </ul>
                        </div>
                        <div class="mb-4">
                            <h6>Assignments</h6>
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>Title</th>
                                            <th>Deadline</th>
                                            <th>Submitted</th>
                                            <th>Pending</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${course.assignments.map(assignment => `
                                            <tr>
                                                <td>${assignment.title}</td>
                                                <td>${formatDate(assignment.deadline)}</td>
                                                <td>${assignment.submitted}</td>
                                                <td>${course.students - assignment.submitted}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div>
                            <h6>Students</h6>
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Name</th>
                                            <th>Attendance</th>
                                            <th>Grades</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${mockData.students[course.code]?.map(student => `
                                            <tr>
                                                <td>${student.id}</td>
                                                <td>${student.name}</td>
                                                <td>${student.attendance}%</td>
                                                <td>
                                                    Midterm: ${student.grades.midterm}%<br>
                                                    Assignments: ${student.grades.assignments}%
                                                </td>
                                            </tr>
                                        `).join('') || '<tr><td colspan="4">No students enrolled</td></tr>'}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Initialize and show modal
    const modal = new bootstrap.Modal(document.getElementById('viewCourseModal'));
    modal.show();

    // Cleanup on modal close
    document.getElementById('viewCourseModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function editCourse(courseId) {
    const course = mockData.courses.find(c => c.id === courseId);
    if (!course) return;

    const modalHtml = `
        <div class="modal fade" id="editCourseModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Course: ${course.code}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editCourseForm">
                            <div class="mb-3">
                                <label class="form-label">Course Name</label>
                                <input type="text" class="form-control" name="name" value="${course.name}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Schedule</label>
                                <div class="row">
                                    <div class="col">
                                        <select class="form-select" name="day" required>
                                            ${['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map(day => `
                                                <option value="${day}" ${course.schedule.day === day ? 'selected' : ''}>
                                                    ${day}
                                                </option>
                                            `).join('')}
                                        </select>
                                    </div>
                                    <div class="col">
                                        <input type="time" class="form-control" name="time" value="${course.schedule.time}" required>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Room</label>
                                <input type="text" class="form-control" name="room" value="${course.schedule.room}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Syllabus Topics</label>
                                <div id="syllabusTopics">
                                    ${course.syllabus.map(topic => `
                                        <div class="input-group mb-2">
                                            <input type="text" class="form-control" name="syllabus[]" value="${topic}" required>
                                            <button type="button" class="btn btn-outline-danger remove-topic">
                                                <i class="fas fa-minus"></i>
                                            </button>
                                        </div>
                                    `).join('')}
                                    <div class="input-group mb-2">
                                        <input type="text" class="form-control" name="syllabus[]">
                                        <button type="button" class="btn btn-outline-secondary add-topic">
                                            <i class="fas fa-plus"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Assignments</label>
                                <div id="assignments">
                                    ${course.assignments.map(assignment => `
                                        <div class="input-group mb-2">
                                            <input type="text" class="form-control" name="assignment_title[]" 
                                                value="${assignment.title}" placeholder="Title" required>
                                            <input type="date" class="form-control" name="assignment_deadline[]" 
                                                value="${assignment.deadline}" required>
                                            <button type="button" class="btn btn-outline-danger remove-assignment">
                                                <i class="fas fa-minus"></i>
                                            </button>
                                        </div>
                                    `).join('')}
                                    <div class="input-group mb-2">
                                        <input type="text" class="form-control" name="assignment_title[]" placeholder="Title">
                                        <input type="date" class="form-control" name="assignment_deadline[]">
                                        <button type="button" class="btn btn-outline-secondary add-assignment">
                                            <i class="fas fa-plus"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="updateCourseBtn">Update Course</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Initialize modal
    const modal = new bootstrap.Modal(document.getElementById('editCourseModal'));
    modal.show();

    // Setup event listeners
    const form = document.getElementById('editCourseForm');
    const updateBtn = document.getElementById('updateCourseBtn');
    const syllabusTopics = document.getElementById('syllabusTopics');
    const assignments = document.getElementById('assignments');

    // Add/remove topic functionality
    syllabusTopics.addEventListener('click', (e) => {
        if (e.target.closest('.add-topic')) {
            const newTopic = `
                <div class="input-group mb-2">
                    <input type="text" class="form-control" name="syllabus[]" required>
                    <button type="button" class="btn btn-outline-danger remove-topic">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            `;
            e.target.closest('.input-group').insertAdjacentHTML('beforebegin', newTopic);
        } else if (e.target.closest('.remove-topic')) {
            e.target.closest('.input-group').remove();
        }
    });

    // Add/remove assignment functionality
    assignments.addEventListener('click', (e) => {
        if (e.target.closest('.add-assignment')) {
            const newAssignment = `
                <div class="input-group mb-2">
                    <input type="text" class="form-control" name="assignment_title[]" placeholder="Title" required>
                    <input type="date" class="form-control" name="assignment_deadline[]" required>
                    <button type="button" class="btn btn-outline-danger remove-assignment">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            `;
            e.target.closest('.input-group').insertAdjacentHTML('beforebegin', newAssignment);
        } else if (e.target.closest('.remove-assignment')) {
            e.target.closest('.input-group').remove();
        }
    });

    // Update course
    updateBtn.addEventListener('click', () => {
        if (form.checkValidity()) {
            const formData = new FormData(form);
            
            // Update course data
            course.name = formData.get('name');
            course.schedule = {
                day: formData.get('day'),
                time: formData.get('time'),
                room: formData.get('room')
            };
            
            // Update syllabus
            course.syllabus = Array.from(formData.getAll('syllabus[]')).filter(topic => topic.trim() !== '');
            
            // Update assignments
            const titles = formData.getAll('assignment_title[]');
            const deadlines = formData.getAll('assignment_deadline[]');
            course.assignments = titles.map((title, index) => {
                if (title.trim() === '' || !deadlines[index]) return null;
                return {
                    title: title,
                    deadline: deadlines[index],
                    submitted: course.assignments[index]?.submitted || 0
                };
            }).filter(assignment => assignment !== null);

            // Close modal and refresh
            modal.hide();
            document.getElementById('editCourseModal').remove();
            loadSection('courses');
            showAlert('Course updated successfully', 'success');
        } else {
            form.reportValidity();
        }
    });

    // Cleanup on modal close
    document.getElementById('editCourseModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

// Add Assignment Modal
function showAddAssignmentModal() {
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="modal fade" id="addAssignmentModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Assignment</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addAssignmentForm">
                            <div class="mb-3">
                                <label class="form-label">Title</label>
                                <input type="text" class="form-control" name="title" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Course</label>
                                <select class="form-select" name="courseId" required>
                                    <option value="">Select Course</option>
                                    ${facultyData.courses.map(course => `
                                        <option value="${course.id}">${course.code} - ${course.name}</option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" name="description" rows="3" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Due Date</label>
                                <input type="date" class="form-control" name="dueDate" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="addAssignment()">Add Assignment</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    new bootstrap.Modal(document.getElementById('addAssignmentModal')).show();
}

// Add Assignment Function
function addAssignment() {
    const form = document.getElementById('addAssignmentForm');
    if (form.checkValidity()) {
        const formData = new FormData(form);
        const assignment = {
            id: Date.now().toString(),
            title: formData.get('title'),
            courseId: formData.get('courseId'),
            description: formData.get('description'),
            dueDate: formData.get('dueDate'),
            createdAt: new Date().toISOString()
        };

        facultyData.assignments.push(assignment);
        saveData('facultyAssignments', facultyData.assignments);
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('addAssignmentModal'));
        modal.hide();
        showAlert('Success', 'Assignment added successfully');
        loadSection('dashboard');
    } else {
        form.reportValidity();
    }
}

// Add News Modal
function showAddNewsModal() {
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="modal fade" id="addNewsModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add News</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addNewsForm">
                            <div class="mb-3">
                                <label class="form-label">Title</label>
                                <input type="text" class="form-control" name="title" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Content</label>
                                <textarea class="form-control" name="content" rows="4" required></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="addNews()">Add News</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    new bootstrap.Modal(document.getElementById('addNewsModal')).show();
}

// Add News Function
function addNews() {
    const form = document.getElementById('addNewsForm');
    if (form.checkValidity()) {
        const formData = new FormData(form);
        const news = {
            id: Date.now().toString(),
            title: formData.get('title'),
            content: formData.get('content'),
            date: new Date().toISOString(),
            createdAt: new Date().toISOString()
        };

        facultyData.news.push(news);
        saveData('facultyNews', facultyData.news);
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('addNewsModal'));
        modal.hide();
        showAlert('Success', 'News added successfully');
        loadSection('dashboard');
    } else {
        form.reportValidity();
    }
}

// Add new section for faculty-student interaction
function generateInteractionsContent() {
    return `
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Student Interactions</h2>
                <div>
                    <button class="btn btn-primary me-2" onclick="showOfficeHoursModal()">
                        <i class="fas fa-clock"></i> Set Office Hours
                    </button>
                    <button class="btn btn-success" onclick="showMessageModal()">
                        <i class="fas fa-envelope"></i> Send Message
                    </button>
                </div>
            </div>

            <!-- Office Hours Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Office Hours Schedule</h5>
                </div>
                <div class="card-body">
                    <div id="officeHoursDisplay">
                        ${getOfficeHours()}
                    </div>
                </div>
            </div>

            <!-- Messages and Interactions -->
            <div class="row">
                <!-- Student Messages -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="mb-0">Student Messages</h5>
                        </div>
                        <div class="card-body">
                            <div class="messages-container">
                                ${getStudentMessages()}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Student Feedback -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="mb-0">Student Feedback</h5>
                        </div>
                        <div class="card-body">
                            <div class="feedback-container">
                                ${getStudentFeedback()}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Course-specific Interactions -->
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Course Interactions</h5>
                </div>
                <div class="card-body">
                    ${facultyData.courses.map(course => `
                        <div class="course-interaction mb-4">
                            <h6>${course.code} - ${course.name}</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar" role="progressbar" 
                                    style="width: ${getCourseInteractionRate(course.id)}%" 
                                    aria-valuenow="${getCourseInteractionRate(course.id)}" 
                                    aria-valuemin="0" 
                                    aria-valuemax="100">
                                    ${getCourseInteractionRate(course.id)}% Interaction Rate
                                </div>
                            </div>
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-outline-primary" 
                                    onclick="showCourseDiscussion('${course.id}')">
                                    <i class="fas fa-comments"></i> Discussion
                                </button>
                                <button class="btn btn-sm btn-outline-success" 
                                    onclick="showStudentProgress('${course.id}')">
                                    <i class="fas fa-chart-line"></i> Progress
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// Helper functions for faculty-student interaction
function getOfficeHours() {
    const officeHours = JSON.parse(localStorage.getItem('facultyOfficeHours') || '[]');
    if (officeHours.length === 0) {
        return '<p class="text-muted">No office hours set. Click "Set Office Hours" to add your availability.</p>';
    }

    return `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Day</th>
                        <th>Time</th>
                        <th>Location</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${officeHours.map(hour => `
                        <tr>
                            <td>${hour.day}</td>
                            <td>${hour.startTime} - ${hour.endTime}</td>
                            <td>${hour.location}</td>
                            <td>
                                <span class="badge bg-${hour.isAvailable ? 'success' : 'warning'}">
                                    ${hour.isAvailable ? 'Available' : 'Booked'}
                                </span>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function getStudentMessages() {
    const messages = JSON.parse(localStorage.getItem('studentMessages') || '[]');
    if (messages.length === 0) {
        return '<p class="text-muted">No messages from students.</p>';
    }

    return `
        <div class="messages-list">
            ${messages.map(message => `
                <div class="message-item mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <h6 class="mb-1">${message.studentName}</h6>
                        <small class="text-muted">${new Date(message.timestamp).toLocaleString()}</small>
                    </div>
                    <p class="mb-1">${message.content}</p>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary" 
                            onclick="replyToMessage('${message.id}')">
                            Reply
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" 
                            onclick="markAsResolved('${message.id}')">
                            Mark as Resolved
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function getStudentFeedback() {
    const feedback = JSON.parse(localStorage.getItem('studentFeedback') || '[]');
    if (feedback.length === 0) {
        return '<p class="text-muted">No feedback received yet.</p>';
    }

    return `
        <div class="feedback-list">
            ${feedback.map(item => `
                <div class="feedback-item mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <h6 class="mb-1">${item.courseCode}</h6>
                        <small class="text-muted">${new Date(item.timestamp).toLocaleString()}</small>
                    </div>
                    <p class="mb-1">${item.content}</p>
                    <div class="rating mb-2">
                        ${'★'.repeat(item.rating)}${'☆'.repeat(5-item.rating)}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function getCourseInteractionRate(courseId) {
    const course = facultyData.courses.find(c => c.id === courseId);
    if (!course) return 0;

    const interactions = JSON.parse(localStorage.getItem(`courseInteractions_${courseId}`) || '[]');
    const totalStudents = course.students?.length || 0;
    if (totalStudents === 0) return 0;

    return Math.round((interactions.length / totalStudents) * 100);
}

// Modal functions for faculty-student interaction
function showOfficeHoursModal() {
    const modalHtml = `
        <div class="modal fade" id="officeHoursModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Set Office Hours</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="officeHoursForm">
                            <div class="mb-3">
                                <label class="form-label">Day of Week</label>
                                <select class="form-select" name="day" required>
                                    <option value="Monday">Monday</option>
                                    <option value="Tuesday">Tuesday</option>
                                    <option value="Wednesday">Wednesday</option>
                                    <option value="Thursday">Thursday</option>
                                    <option value="Friday">Friday</option>
                                </select>
                            </div>
                            <div class="row mb-3">
                                <div class="col">
                                    <label class="form-label">Start Time</label>
                                    <input type="time" class="form-control" name="startTime" required>
                                </div>
                                <div class="col">
                                    <label class="form-label">End Time</label>
                                    <input type="time" class="form-control" name="endTime" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Location</label>
                                <input type="text" class="form-control" name="location" required>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="isAvailable" checked>
                                    <label class="form-check-label">Available for Booking</label>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="saveOfficeHours()">Save</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('officeHoursModal'));
    modal.show();
}

function showMessageModal() {
    const modalHtml = `
        <div class="modal fade" id="messageModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Send Message to Students</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="messageForm">
                            <div class="mb-3">
                                <label class="form-label">Course</label>
                                <select class="form-select" name="courseId" required>
                                    <option value="">Select Course</option>
                                    ${facultyData.courses.map(course => `
                                        <option value="${course.id}">${course.code} - ${course.name}</option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Message Type</label>
                                <select class="form-select" name="messageType" required>
                                    <option value="announcement">Announcement</option>
                                    <option value="reminder">Reminder</option>
                                    <option value="feedback">Feedback Request</option>
                                </select>
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

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('messageModal'));
    modal.show();
}

// Save functions for faculty-student interaction
function saveOfficeHours() {
    const form = document.getElementById('officeHoursForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const officeHour = {
        id: Date.now().toString(),
        day: formData.get('day'),
        startTime: formData.get('startTime'),
        endTime: formData.get('endTime'),
        location: formData.get('location'),
        isAvailable: formData.get('isAvailable') === 'on',
        createdAt: new Date().toISOString()
    };

    // Save to localStorage
    const officeHours = JSON.parse(localStorage.getItem('facultyOfficeHours') || '[]');
    officeHours.push(officeHour);
    localStorage.setItem('facultyOfficeHours', JSON.stringify(officeHours));

    // Close modal and refresh
    const modal = bootstrap.Modal.getInstance(document.getElementById('officeHoursModal'));
    modal.hide();
    showAlert('Success', 'Office hours saved successfully');
    loadSection('interactions');
}

function sendMessage() {
    const form = document.getElementById('messageForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const message = {
        id: Date.now().toString(),
        courseId: formData.get('courseId'),
        type: formData.get('messageType'),
        content: formData.get('message'),
        sender: userData.full_name,
        timestamp: new Date().toISOString()
    };

    // Save to localStorage
    const messages = JSON.parse(localStorage.getItem('facultyMessages') || '[]');
    messages.push(message);
    localStorage.setItem('facultyMessages', JSON.stringify(messages));

    // Close modal and refresh
    const modal = bootstrap.Modal.getInstance(document.getElementById('messageModal'));
    modal.hide();
    showAlert('Success', 'Message sent successfully');
    loadSection('interactions');
} 