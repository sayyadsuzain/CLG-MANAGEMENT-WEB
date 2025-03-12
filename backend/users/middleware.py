from django.http import JsonResponse
from django.urls import resolve
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils import get_redirect_url_by_role
import time
import logging

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        # Skip authentication for auth-related endpoints
        current_url = resolve(request.path_info).url_name
        auth_endpoints = ['login', 'signup', 'verify_email', 'resend_verification']
        
        if current_url in auth_endpoints:
            return self.get_response(request)

        # Try to authenticate using JWT
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                user, token = self.jwt_auth.authenticate(request)
                if user:
                    request.user = user
                    # Add role-based data to request
                    redirect_data = get_redirect_url_by_role(user)
                    request.user_role_data = redirect_data
                    return self.get_response(request)
            
            # If no valid token is found, return unauthorized
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
            
        except Exception as e:
            return JsonResponse(
                {'error': str(e)},
                status=401
            )

class RoleBasedAccessMiddleware:
    """
    Middleware to handle role-based access control
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for auth endpoints and OPTIONS requests
        if request.method == 'OPTIONS' or not request.user.is_authenticated:
            return self.get_response(request)

        current_url = resolve(request.path_info).url_name
        user_role_data = getattr(request, 'user_role_data', {})
        user_permissions = user_role_data.get('permissions', [])

        # Allow superusers to access everything
        if request.user.is_superuser or 'all' in user_permissions:
            return self.get_response(request)

        # Define role-based URL patterns
        role_patterns = {
            'student': [
                'student_dashboard',
                'view_courses',
                'submit_assignment',
                'view_grades',
                'view_attendance',
                'register_event'
            ],
            'faculty': [
                'faculty_dashboard',
                'manage_courses',
                'create_assignment',
                'grade_submission',
                'mark_attendance',
                'create_notice'
            ]
        }

        user_role = user_role_data.get('role')
        allowed_urls = role_patterns.get(user_role, [])

        # Check if the current URL is allowed for the user's role
        if current_url not in allowed_urls and not any(
            perm in current_url for perm in user_permissions
        ):
            return JsonResponse(
                {'error': 'Access denied'},
                status=403
            )

        return self.get_response(request)

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('django.request')

    def __call__(self, request):
        # Start timing the request
        start_time = time.time()

        # Add request to logging context
        request.logging_context = {
            'request': request,
            'start_time': start_time,
        }

        try:
            response = self.get_response(request)
            self.log_response(request, response, start_time)
            return response
        except Exception as e:
            self.log_exception(request, e, start_time)
            raise

    def log_response(self, request, response, start_time):
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Add extra information to the log record
        extra = {
            'request': request,
            'response_status': response.status_code,
            'execution_time': execution_time,
        }

        # Log based on response status
        if response.status_code >= 500:
            self.logger.error(
                f"Server error ({response.status_code}): {request.path}",
                extra=extra
            )
        elif response.status_code >= 400:
            self.logger.warning(
                f"Client error ({response.status_code}): {request.path}",
                extra=extra
            )
        else:
            self.logger.info(
                f"Request completed ({response.status_code}): {request.path}",
                extra=extra
            )

    def log_exception(self, request, exception, start_time):
        execution_time = (time.time() - start_time) * 1000
        self.logger.error(
            f"Exception during request: {str(exception)}",
            exc_info=True,
            extra={
                'request': request,
                'execution_time': execution_time,
            }
        ) 