from lib2to3.refactor import MultiprocessingUnsupported
from django.db import models


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
    
