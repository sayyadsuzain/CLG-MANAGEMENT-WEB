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
- **Secure Communication**: SSL/TLS support for secure data transmission
- **Excel Export**: Support for exporting data to Excel format

## Technology Stack

- **Backend**: Django 5.0.2
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite (default), can be configured for PostgreSQL or MySQL
- **Authentication**: Django's built-in authentication system
- **WebSocket Support**: Channels and Daphne for real-time features
- **SSL/TLS**: Built-in SSL support for secure communication

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

6. Configure SSL (Required for HTTPS):
   
   ```
   # Generate self-signed certificates (for development)
   mkdir ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/private.key -out ssl/certificate.crt
   
   # Set proper permissions
   chmod 600 ssl/private.key
   chmod 644 ssl/certificate.crt
   ```

7. Run the production server with SSL:

   ```
   daphne -e ssl:8443:privateKey=ssl/private.key:certKey=ssl/certificate.crt college_management.asgi:application
   ```

8. Access the application at https://localhost:8443/

## Configuration

### SSL Configuration
- Place your SSL certificates in the `ssl` directory
- For production, use properly signed certificates from a trusted CA
- Update certificate paths in the Daphne command if needed

### Environment Variables
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Configure allowed hostnames
- `SECRET_KEY`: Set a secure secret key

## Usage

### For Administrators

- Create faculty and student accounts
- Manage courses and departments
- Generate reports
- Monitor system logs

### For Faculty

- Create and manage courses
- Mark attendance
- Upload course materials
- Create assignments and grade students
- Post notices
- Export attendance and grades to Excel

### For Students

- View enrolled courses
- Check attendance status
- Submit assignments
- View grades
- Access course materials
- Receive real-time notifications

## Security Features

- CSRF protection enabled
- SSL/TLS encryption
- Secure password hashing
- Session management
- Permission-based access control

## Troubleshooting

1. SSL Certificate Issues:
   - Accept self-signed certificates in development
   - Ensure proper certificate permissions
   - Check certificate paths in Daphne command

2. Port Already in Use:
   - Kill existing processes: `pkill -f daphne`
   - Choose a different port if needed

3. Permission Issues:
   - Check file permissions for SSL certificates
   - Ensure proper ownership of project files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
