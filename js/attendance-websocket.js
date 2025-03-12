// WebSocket connection handler for attendance updates
class AttendanceWebSocket {
    constructor(studentEmail) {
        this.studentEmail = studentEmail;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 5000; // 5 seconds
        
        this.connect();
    }
    
    connect() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/attendance/${this.studentEmail}/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connection established');
            this.reconnectAttempts = 0;
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
            this.handleReconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'attendance_update':
                // Refresh attendance data
                loadAttendanceData();
                
                // Show notification
                showAlert('Update', `Attendance marked by ${data.faculty_name} for ${data.course_name}`);
                
                // Update attendance statistics
                this.updateAttendanceStats(data);
                break;
                
            case 'attendance_reminder':
                // Show reminder notification
                showAlert('Reminder', data.message);
                break;
                
            case 'attendance_warning':
                // Show warning for low attendance
                showAlert('Warning', data.message, 'warning');
                break;
        }
    }
    
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            showAlert('Error', 'Lost connection to attendance updates. Please refresh the page.', 'error');
        }
    }
    
    updateAttendanceStats(data) {
        const attendanceKey = `attendance_${data.course_id}`;
        const attendanceData = JSON.parse(localStorage.getItem(attendanceKey) || '{}');
        
        // Add new attendance record
        const newRecord = {
            date: new Date(data.date),
            present: data.status === 'present',
            markedByName: data.faculty_name,
            markedByEmail: data.faculty_email,
            markedAt: new Date()
        };
        
        attendanceData.records = attendanceData.records || [];
        attendanceData.records.push(newRecord);
        
        // Update localStorage
        localStorage.setItem(attendanceKey, JSON.stringify(attendanceData));
        
        // Update UI
        const attendanceElement = document.querySelector(`[data-course-id="${data.course_id}"]`);
        if (attendanceElement) {
            const attendance = getAttendanceForCourse(data.course_id);
            attendanceElement.querySelector('.attendance-percentage').textContent = `${attendance.percentage}%`;
            attendanceElement.querySelector('.attendance-progress').style.width = `${attendance.percentage}%`;
        }
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Initialize WebSocket connection
let attendanceSocket = null;

function initializeAttendanceWebSocket() {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    if (userData.email) {
        attendanceSocket = new AttendanceWebSocket(userData.email);
    }
}

// Cleanup on page unload
window.addEventListener('unload', () => {
    if (attendanceSocket) {
        attendanceSocket.disconnect();
    }
}); 