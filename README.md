# College Management System

A comprehensive web-based system for managing college operations including attendance tracking, course management, grade management, and communication between faculty and students.

## Features

- **User Authentication**: Secure login for students, faculty, and administrators
- **Course Management**: Create, update, and manage courses
- **Attendance Tracking**: Mark and track student attendance with detailed reports
- **Grade Management**: Record and manage student grades
- **Notice Board**: Share important announcements with students
- **Resource Sharing**: Upload and share course materials
- **Notifications**: Automated notifications for important events

## Technology Stack

- **Backend**: Django 5.0.2
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite (default), can be configured for PostgreSQL or MySQL
- **Authentication**: Django's built-in authentication system

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/college-management-system.git
   cd college-management-system
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Usage

### For Administrators
- Create faculty and student accounts
- Manage courses and departments
- Generate reports

### For Faculty
- Create and manage courses
- Mark attendance
- Upload course materials
- Create assignments and grade students
- Post notices

### For Students
- View enrolled courses
- Check attendance status
- Submit assignments
- View grades
- Access course materials

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
