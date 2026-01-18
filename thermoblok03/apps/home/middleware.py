import logging
from django.http import HttpResponseServerError
from django.conf import settings

logger = logging.getLogger(__name__)

class ErrorLoggingMiddleware:
    """Middleware для логирования ошибок"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Обработка исключений"""
        # Логируем ошибку
        logger.error(
            f'Error processing request {request.path}: {exception}',
            exc_info=True,
            extra={
                'request': request,
                'user': request.user if hasattr(request, 'user') else None,
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
            }
        )
        
        # Отправляем уведомление администратору (если настроено)
        if not settings.DEBUG:
            self.notify_admin(request, exception)
        
        return None
    
    def notify_admin(self, request, exception):
        """Отправка уведомления администратору"""
        # Здесь можно реализовать отправку email, в Telegram и т.д.
        pass