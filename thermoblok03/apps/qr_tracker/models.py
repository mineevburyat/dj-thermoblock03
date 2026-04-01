# models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

class TrackedLink(models.Model):
    """Модель для отслеживаемых ссылок"""
    slug = models.SlugField(
        max_length=50, 
        unique=True,
        help_text="Уникальный идентификатор для QR-кода"
    )
    name = models.CharField(
        max_length=200,
        help_text="Название ссылки (для админки)"
    )
    target_url = models.URLField(
        max_length=2000,
        help_text="Конечный URL для перехода"
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        help_text="Загрузите готовый QR-код (PNG, JPEG, SVG)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Статистика
    total_clicks = models.PositiveIntegerField(default=0)
    unique_clicks = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.slug})"
    
    def get_absolute_url(self):
        """Возвращает URL для редиректа"""
        return reverse('qr_tracker:redirect', kwargs={'slug': self.slug})
    
    def get_qr_data(self):
        """Возвращает данные для QR-кода (полный URL)"""
        return f"{settings.BASE_URL}{self.get_absolute_url()}"
    
    def increment_click(self, request):
        """Увеличить счетчик переходов и записать детали"""
        self.total_clicks += 1
        
        # Проверяем уникальность по сессии или IP
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            
        if not ClickLog.objects.filter(
            link=self, 
            session_key=session_key
        ).exists():
            self.unique_clicks += 1
        
        self.save()
        
        # Записываем детали перехода
        ClickLog.objects.create(
            link=self,
            session_key=session_key,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referer=request.META.get('HTTP_REFERER', ''),
        )
    
    @staticmethod
    def get_client_ip(request):
        """Получить IP адрес клиента с учетом прокси"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ClickLog(models.Model):
    """Детальная статистика каждого перехода"""
    link = models.ForeignKey(
        TrackedLink, 
        on_delete=models.CASCADE,
        related_name='clicks'
    )
    clicked_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField()
    referer = models.URLField(max_length=2000, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['link', 'clicked_at']),
            models.Index(fields=['session_key']),
        ]
        ordering = ['-clicked_at']
    
    def __str__(self):
        return f"{self.link.name} - {self.clicked_at}"