import mockDatabase from './mock-data.js';

class ApiService {
    constructor() {
        this.baseUrl = 'http://localhost:8000/api';
        this.mockMode = true; // Toggle between mock and real API
    }

    // Authentication
    async login(credentials) {
        if (this.mockMode) {
            const { email, password } = credentials;
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Mock authentication
            if (email === "faculty@college.edu" && password === "password123") {
                return {
                    token: "mock_faculty_token",
                    user: mockDatabase.faculty[0],
                    role: "faculty"
                };
            } else if (email === "student@college.edu" && password === "password123") {
                return {
                    token: "mock_student_token",
                    user: mockDatabase.students[0],
                    role: "student"
                };
            }
            throw new Error("Invalid credentials");
        }
        
        return this.makeRequest('/auth/login', {
            method: 'POST',
            body: credentials
        });
    }

    // Profile Management
    async getUserProfile(userId, role) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 500));
            return role === 'faculty' 
                ? mockDatabase.faculty.find(f => f.id === userId)
                : mockDatabase.students.find(s => s.id === userId);
        }
        return this.makeRequest(`/users/${userId}/profile`);
    }

    // Course Management
    async getCourses(userId, role) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 600));
            if (role === 'faculty') {
                return mockDatabase.courses.filter(c => c.faculty === userId);
            } else {
                const student = mockDatabase.students.find(s => s.id === userId);
                return mockDatabase.courses.filter(c => student.courses.includes(c.id));
            }
        }
        return this.makeRequest(`/${role}/courses`);
    }

    // Attendance Management
    async getAttendance(courseId, date) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 400));
            return mockDatabase.attendance[courseId] || {
                date: date,
                present: [],
                absent: [],
                total: 0
            };
        }
        return this.makeRequest(`/attendance/${courseId}?date=${date}`);
    }

    async markAttendance(courseId, data) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 600));
            mockDatabase.attendance[courseId] = {
                ...mockDatabase.attendance[courseId],
                ...data
            };
            return { success: true };
        }
        return this.makeRequest(`/attendance/${courseId}`, {
            method: 'POST',
            body: data
        });
    }

    // Assignment Management
    async getAssignments(courseId) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 500));
            return mockDatabase.assignments.filter(a => a.courseId === courseId);
        }
        return this.makeRequest(`/courses/${courseId}/assignments`);
    }

    async createAssignment(data) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 700));
            const newAssignment = {
                id: `ASG${Date.now()}`,
                ...data,
                submissions: {}
            };
            mockDatabase.assignments.push(newAssignment);
            return newAssignment;
        }
        return this.makeRequest('/assignments', {
            method: 'POST',
            body: data
        });
    }

    // Notice Board
    async getNotices(department) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 400));
            return mockDatabase.notices.filter(n => 
                !department || n.department === department
            );
        }
        return this.makeRequest(`/notices?department=${department}`);
    }

    async createNotice(data) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 600));
            const newNotice = {
                id: `NOT${Date.now()}`,
                postedDate: new Date().toISOString(),
                ...data
            };
            mockDatabase.notices.push(newNotice);
            return newNotice;
        }
        return this.makeRequest('/notices', {
            method: 'POST',
            body: data
        });
    }

    // Grade Management
    async getGrades(studentId, courseId) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 500));
            return mockDatabase.grades[studentId]?.[courseId] || {
                assignments: 0,
                midterm: 0,
                final: 0,
                total: 0,
                grade: 'N/A'
            };
        }
        return this.makeRequest(`/grades/${studentId}/${courseId}`);
    }

    async updateGrades(studentId, courseId, data) {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 700));
            if (!mockDatabase.grades[studentId]) {
                mockDatabase.grades[studentId] = {};
            }
            mockDatabase.grades[studentId][courseId] = {
                ...mockDatabase.grades[studentId][courseId],
                ...data
            };
            return { success: true };
        }
        return this.makeRequest(`/grades/${studentId}/${courseId}`, {
            method: 'PUT',
            body: data
        });
    }

    // Events
    async getEvents() {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 400));
            return mockDatabase.events;
        }
        return this.makeRequest('/events');
    }

    // Library
    async getLibraryBooks(query = '') {
        if (this.mockMode) {
            await new Promise(resolve => setTimeout(resolve, 600));
            return mockDatabase.library.books.filter(book => 
                book.title.toLowerCase().includes(query.toLowerCase()) ||
                book.author.toLowerCase().includes(query.toLowerCase())
            );
        }
        return this.makeRequest(`/library/books?query=${query}`);
    }

    // Helper method for making real API requests
    async makeRequest(endpoint, options = {}) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : '',
                    ...options.headers
                },
                body: options.body ? JSON.stringify(options.body) : undefined
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }
}

// Create and export a single instance
const apiService = new ApiService();
export default apiService; 