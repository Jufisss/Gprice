import logging

logger = logging.getLogger(__name__)

class CSRFDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Логируем CSRF информацию
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            logger.info(f"CSRF Debug - Method: {request.method}")
            logger.info(f"CSRF Debug - Headers: {dict(request.headers)}")
            logger.info(f"CSRF Debug - COOKIES: {request.COOKIES}")
            logger.info(f"CSRF Debug - CSRF_COOKIE: {request.META.get('CSRF_COOKIE')}")
            logger.info(f"CSRF Debug - HTTP_X_CSRFTOKEN: {request.META.get('HTTP_X_CSRFTOKEN')}")
        
        response = self.get_response(request)
        return response