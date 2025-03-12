// Mock Database
const mockDatabase = {
    students: [
        {
            id: "STU2024001",
            name: "John Smith",
            email: "john.smith@college.edu",
            department: "Computer Science",
            semester: 6,
            enrollmentYear: 2021,
            cgpa: 3.75,
            attendance: 85,
            courses: ["CS301", "CS302", "CS303", "MTH301"],
            contact: "+1 234-567-8901",
            address: "123 College Ave, Boston, MA 02115",
            guardianName: "Mary Smith",
            guardianContact: "+1 234-567-8902"
        },
        // More realistic student entries...
    ],

    faculty: [
        {
            id: "FAC2024001",
            name: "Dr. Sarah Johnson",
            email: "sarah.johnson@college.edu",
            department: "Computer Science",
            designation: "Associate Professor",
            specialization: "Machine Learning",
            joinDate: "2020-01-15",
            courses: ["CS301", "CS405"],
            education: {
                phd: "MIT - Artificial Intelligence (2018)",
                masters: "Stanford - Computer Science (2014)"
            },
            contact: "+1 234-567-8900",
            office: "Room 405, CS Building"
        },
        // More faculty entries...
    ],

    courses: [
        {
            id: "CS301",
            name: "Advanced Database Systems",
            credits: 4,
            department: "Computer Science",
            semester: 6,
            faculty: "FAC2024001",
            schedule: {
                days: ["Monday", "Wednesday"],
                time: "10:00 AM - 11:30 AM",
                room: "CS Lab 2"
            },
            prerequisites: ["CS201", "CS202"],
            maxStudents: 40,
            enrolledStudents: 38
        },
        // More course entries...
    ],

    attendance: {
        "CS301": {
            date: "2024-03-15",
            present: ["STU2024001", "STU2024003"],
            absent: ["STU2024002"],
            total: 38
        },
        // More attendance records...
    },

    assignments: [
        {
            id: "ASG2024001",
            courseId: "CS301",
            title: "Database Normalization Project",
            description: "Implement a database system following 3NF normalization...",
            dueDate: "2024-03-25T23:59:59",
            totalMarks: 100,
            weightage: 20,
            submissions: {
                "STU2024001": {
                    submissionDate: "2024-03-20T14:30:00",
                    status: "submitted",
                    marks: 85
                }
            }
        },
        // More assignments...
    ],

    examSchedule: [
        {
            id: "EXAM2024001",
            courseId: "CS301",
            type: "Mid-term",
            date: "2024-03-30",
            time: "09:00 AM - 11:00 AM",
            venue: "Examination Hall A",
            totalMarks: 50
        },
        // More exam schedules...
    ],

    notices: [
        {
            id: "NOT2024001",
            title: "Mid-term Examination Schedule",
            content: "The mid-term examinations for Spring 2024 will commence from March 30th...",
            department: "Computer Science",
            postedBy: "FAC2024001",
            postedDate: "2024-03-15T10:00:00",
            priority: "high",
            attachments: ["schedule.pdf"]
        },
        // More notices...
    ],

    departments: [
        {
            id: "DEP001",
            name: "Computer Science",
            head: "FAC2024005",
            totalStudents: 245,
            totalFaculty: 12,
            courses: ["CS301", "CS302", "CS303"],
            location: "Building A, Floor 4"
        },
        // More departments...
    ],

    timetable: {
        "CS-6": {  // 6th semester CS
            Monday: [
                {
                    courseId: "CS301",
                    time: "10:00 AM - 11:30 AM",
                    room: "CS Lab 2"
                },
                // More Monday classes...
            ],
            // More days...
        },
        // More semester timetables...
    },

    grades: {
        "STU2024001": {
            "CS301": {
                assignments: 85,
                midterm: 78,
                final: 88,
                total: 84,
                grade: "A"
            },
            // More course grades...
        },
        // More student grades...
    },

    events: [
        {
            id: "EVT2024001",
            title: "Technical Symposium 2024",
            description: "Annual technical fest featuring workshops, competitions...",
            startDate: "2024-04-15",
            endDate: "2024-04-17",
            venue: "College Auditorium",
            organizer: "Computer Science Department",
            registrationDeadline: "2024-04-10"
        },
        // More events...
    ],

    library: {
        books: [
            {
                id: "BK001",
                title: "Database Management Systems",
                author: "Ramakrishnan",
                isbn: "978-0123456789",
                copies: 5,
                available: 3
            },
            // More books...
        ],
        transactions: [
            {
                id: "TR001",
                bookId: "BK001",
                studentId: "STU2024001",
                issueDate: "2024-03-01",
                dueDate: "2024-03-15",
                returnDate: null,
                status: "issued"
            },
            // More transactions...
        ]
    }
};

// Helper functions for data access
const getStudentById = (id) => mockDatabase.students.find(s => s.id === id);
const getFacultyById = (id) => mockDatabase.faculty.find(f => f.id === id);
const getCourseById = (id) => mockDatabase.courses.find(c => c.id === id);

// Export the mock database
export default mockDatabase; 