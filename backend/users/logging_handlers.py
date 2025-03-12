import logging
import traceback
from django.conf import settings
from django.utils.module_loading import import_string
from .models import Log

class DatabaseLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.model = Log

    def emit(self, record):
        try:
            # Get the request from the record if available
            request = getattr(record, 'request', None)
            user = None
            ip_address = None
            request_method = None
            request_path = None
            request_body = None
            response_status = None

            if request:
                # Get user if authenticated
                user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                
                # Get IP address
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
                
                # Get request details
                request_method = request.method
                request_path = request.path
                request_body = request.body.decode('utf-8') if request.body else None
                
                # Get response status if available
                response_status = getattr(record, 'response_status', None)

            # Get execution time if available
            execution_time = getattr(record, 'execution_time', None)

            # Create the log entry
            self.model.objects.create(
                logger_name=record.name,
                level=record.levelname,
                message=self.format(record),
                file_path=record.pathname,
                function_name=record.funcName,
                line_number=record.lineno,
                exception=record.exc_info[1] if record.exc_info else None,
                stack_trace=''.join(traceback.format_exception(*record.exc_info)) if record.exc_info else None,
                user=user,
                ip_address=ip_address,
                request_method=request_method,
                request_path=request_path,
                request_body=request_body,
                response_status=response_status,
                execution_time=execution_time
            )
        except Exception as e:
            # If there's an error logging to the database, log to the console
            print(f"Error logging to database: {str(e)}") 