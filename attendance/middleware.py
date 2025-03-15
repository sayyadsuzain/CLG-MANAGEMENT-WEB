import logging
import json
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('attendance')

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request details
        log_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user),
            'ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
        }
        
        # Log request body for POST/PUT requests (excluding sensitive data)
        if request.method in ['POST', 'PUT'] and not any(sensitive in request.path for sensitive in ['/login', '/password']):
            try:
                body = request.body.decode('utf-8')
                if body:
                    try:
                        body_data = json.loads(body)
                        # Remove sensitive fields if present
                        for sensitive_field in ['password', 'token', 'key']:
                            if sensitive_field in body_data:
                                body_data[sensitive_field] = '[REDACTED]'
                        log_data['body'] = body_data
                    except json.JSONDecodeError:
                        log_data['body'] = '[non-JSON body]'
            except Exception as e:
                logger.debug(f'Could not decode request body: {str(e)}')
        
        logger.info(f'Request: {json.dumps(log_data)}')
    
    def process_response(self, request, response):
        # Calculate request duration
        duration = time.time() - getattr(request, 'start_time', time.time())
        
        # Log response details
        log_data = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration': f'{duration:.2f}s',
            'content_type': response.get('Content-Type', 'unknown'),
        }
        
        # Log response content for errors
        if response.status_code >= 400:
            try:
                if 'application/json' in response.get('Content-Type', ''):
                    content = json.loads(response.content.decode('utf-8'))
                    log_data['response_body'] = content
                else:
                    log_data['response_body'] = '[non-JSON response]'
            except Exception as e:
                logger.debug(f'Could not decode response content: {str(e)}')
        
        logger.info(f'Response: {json.dumps(log_data)}')
        return response
    
    def process_exception(self, request, exception):
        logger.error(f'Unhandled exception in {request.path}: {str(exception)}', exc_info=True) 