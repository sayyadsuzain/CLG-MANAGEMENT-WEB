import logging
from typing import Optional, Dict, Any
from django.http import HttpRequest
from django.utils import timezone
from django.conf import settings
from .models import UserActivity, User
import user_agents
import json
import socket
import requests
from ipware import get_client_ip
import traceback

logger = logging.getLogger(__name__)

def get_location_from_ip(ip_address: str) -> Optional[str]:
    """Get location information from IP address using ipapi.co service."""
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('city', '')}, {data.get('country_name', '')}"
    except Exception as e:
        logger.warning(f"Failed to get location from IP: {str(e)}")
    return None

def get_client_details(request: HttpRequest) -> Dict[str, Any]:
    """Extract client details from the request object."""
    details = {
        'ip_address': None,
        'user_agent': None,
        'device_type': None,
        'location': None
    }

    try:
        # Get IP address using django-ipware
        client_ip, is_routable = get_client_ip(request)
        if client_ip:
            details['ip_address'] = client_ip
            # Only try to get location if it's a routable IP
            if is_routable and not client_ip.startswith(('127.', '192.168.', '10.')):
                details['location'] = get_location_from_ip(client_ip)

        # Get user agent information
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        if user_agent_string:
            details['user_agent'] = user_agent_string
            user_agent = user_agents.parse(user_agent_string)
            details['device_type'] = {
                'browser': user_agent.browser.family,
                'browser_version': user_agent.browser.version_string,
                'os': user_agent.os.family,
                'os_version': user_agent.os.version_string,
                'device': user_agent.device.family,
                'is_mobile': user_agent.is_mobile,
                'is_tablet': user_agent.is_tablet,
                'is_pc': user_agent.is_pc
            }

    except Exception as e:
        logger.error(f"Error getting client details: {str(e)}")

    return details

def sanitize_extra_data(extra_data: Any) -> Optional[Dict]:
    """Sanitize and validate extra data for JSON storage."""
    if extra_data is None:
        return None
    
    try:
        # If it's already a dict, try to serialize it to catch any JSON issues
        if isinstance(extra_data, dict):
            json.dumps(extra_data)
            return extra_data
        # If it's a string, try to parse it as JSON
        elif isinstance(extra_data, str):
            return json.loads(extra_data)
        # For other types, convert to string and store as message
        else:
            return {'message': str(extra_data)}
    except Exception as e:
        logger.warning(f"Failed to process extra_data: {str(e)}")
        return {'error': 'Invalid extra data format'}

def log_user_activity(
    user: User,
    activity_type: str,
    request: Optional[HttpRequest] = None,
    extra_data: Any = None,
    performed_by: Optional[User] = None
) -> Optional[UserActivity]:
    """
    Log user activity with enhanced information and error handling.
    
    Args:
        user: User object for whom the activity is being logged
        activity_type: Type of activity from UserActivity.ACTIVITY_TYPES
        request: HTTP request object (optional)
        extra_data: Additional data to store (optional)
        performed_by: User who performed the action (for admin actions)
    
    Returns:
        UserActivity object if successful, None if failed
    
    Example:
        # Log a login activity
        log_user_activity(user, 'login', request)
        
        # Log a profile update with extra data
        log_user_activity(
            user,
            'profile_update',
            request,
            {'fields_updated': ['first_name', 'phone_number']}
        )
        
        # Log an admin action
        log_user_activity(
            target_user,
            'account_lock',
            request,
            {'reason': 'Multiple failed login attempts'},
            performed_by=admin_user
        )
    """
    try:
        # Debug logging
        print(f"Attempting to log activity - Type: {activity_type}, User: {user.email}")
        
        # Validate activity type
        valid_activity_types = dict(UserActivity.ACTIVITY_TYPES).keys()
        if activity_type not in valid_activity_types:
            print(f"Invalid activity type: {activity_type}")
            print(f"Valid types are: {valid_activity_types}")
            logger.error(f"Invalid activity type: {activity_type}")
            return None

        # Initialize activity data
        activity_data = {
            'user': user,
            'activity_type': activity_type,
            'performed_by': performed_by or user,
            'extra_data': sanitize_extra_data(extra_data)
        }

        # Get client details if request is provided
        if request:
            client_details = get_client_details(request)
            print(f"Client details: {client_details}")
            activity_data.update(client_details)

            # Add request-specific data to extra_data
            request_data = {
                'method': request.method,
                'path': request.path,
                'referrer': request.META.get('HTTP_REFERER'),
            }
            print(f"Request data: {request_data}")
            
            if activity_data['extra_data'] is None:
                activity_data['extra_data'] = {}
            activity_data['extra_data']['request'] = request_data

        # Create activity log
        print(f"Creating activity log with data: {activity_data}")
        activity = UserActivity.objects.create(**activity_data)
        print(f"Activity log created successfully with ID: {activity.id}")

        # Log to system logger for monitoring
        log_message = (
            f"Activity logged - Type: {activity_type}, "
            f"User: {user.email}, "
            f"IP: {activity_data.get('ip_address')}, "
            f"Location: {activity_data.get('location')}"
        )
        
        if performed_by and performed_by != user:
            log_message += f", Performed by: {performed_by.email}"
        
        logger.info(log_message)

        return activity

    except Exception as e:
        error_message = f"Failed to log user activity: {str(e)}"
        print(f"Error in log_user_activity: {error_message}")
        print(f"Exception details: {traceback.format_exc()}")
        logger.error(error_message)
        if settings.DEBUG:
            raise  # Re-raise the exception in debug mode
        return None

def get_redirect_url_by_role(user):
    """
    Determine the redirect URL based on user role.
    Returns a dictionary containing the redirect URL and any additional data.
    """
    if not user.is_active:
        return {
            'url': '/auth/inactive',
            'message': 'Your account is inactive. Please contact the administrator.'
        }
    
    if user.is_superuser:
        return {
            'url': '/admin/dashboard',
            'role': 'admin',
            'permissions': ['all']
        }
    
    if hasattr(user, 'faculty'):
        return {
            'url': '/faculty/dashboard',
            'role': 'faculty',
            'permissions': [
                'view_courses',
                'manage_assignments',
                'mark_attendance',
                'grade_submissions',
                'create_notices'
            ],
            'faculty_id': user.faculty.id
        }
    
    if hasattr(user, 'student'):
        return {
            'url': '/student/dashboard',
            'role': 'student',
            'permissions': [
                'view_courses',
                'submit_assignments',
                'view_grades',
                'view_attendance',
                'register_events'
            ],
            'student_id': user.student.id,
            'semester': user.student.current_semester
        }
    
    # Default case for authenticated users without specific roles
    return {
        'url': '/dashboard',
        'role': 'user',
        'permissions': ['view_notices', 'view_events']
    } 