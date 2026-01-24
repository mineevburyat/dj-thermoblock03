from django.db import models
from django.utils import timezone

# Create your models here.
class Feedback(models.Model):
    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"

    name = models.CharField(verbose_name='имя посетителя',
                            max_length=50)
    phone = models.CharField(verbose_name='телефон',
                             max_length=20)
    description = models.TextField(verbose_name="дополнения", blank=True, null=True)
    crm_status = models.BooleanField(default=False)
    crm_error = models.TextField(verbose_name="Сообщение об ошибке", blank=True, null=True)
    connect_time = models.DateTimeField(verbose_name='время обращения',
                                        auto_now_add=True)
    ip_address = models.GenericIPAddressField(verbose_name='ip адрес',
                                              blank=True,
                                              null=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"
    

class CalculationRequest(models.Model):
    HOUSE_TYPES = [
        ('одноэтажный', 'Одноэтажный дом'),
        ('двухэтажный', 'Двухэтажный дом'),
        ('с мансардой', 'Дом с мансардой'),
        ('полутороэтажный', 'Полутораэтажный дом'),
        ('гараж', 'Гараж'),
        ('производственное помещение', 'Производственное помещение'),
        ('офис', 'Офисное здание'),
        ('не определился', 'Пока не определился'),
    ]
    
    LAND_STATUSES = [
        ('есть участок', 'Есть участок'),
        ('в процессе покупки', 'В процессе покупки'),
        ('планирую покупать', 'Планирую покупать'),
        ('нужна помощь', 'Нужна помощь в подборе'),
    ]
    
    PROJECT_STATUSES = [
        ('готовый проект', 'Готовый проект'),
        ('есть эскиз', 'Есть эскиз'),
        ('есть наброски', 'Есть эскизы и наброски'),
        ('заказать проект', 'Хочу заказать проект'),
        ('нужна консультация', 'Нужна консультация'),
    ]
    
    TIMELINES = [
        ('как можно скорее', 'Как можно скорее'),
        ('хочу консультацию', 'Хочу сначала проконсультироваться'),
        ('в течении года', 'В течение года'),
        ('3-6 месяцев', 'В течение 3-6 месяцев'),
        ('в этом месяце', 'В течение этого месяца'),
    ]
    
    PAYMENT_METHODS = [
        ('собственные средства', 'Собственные средства'),
        ('ипотека', 'Ипотека'),
    ]
    
    CONTACT_METHODS = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('viber', 'Viber'),
        ('email', 'Email'),
    ]
    
    house_type = models.CharField(max_length=50, choices=HOUSE_TYPES)
    land_status = models.CharField(max_length=50, choices=LAND_STATUSES)
    project_status = models.CharField(max_length=50, choices=PROJECT_STATUSES)
    timeline = models.CharField(max_length=50, choices=TIMELINES)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    contact_method = models.CharField(max_length=50, choices=CONTACT_METHODS)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    comments = models.TextField(blank=True)
    data_agreement = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявка от {self.name} - {self.house_type}"