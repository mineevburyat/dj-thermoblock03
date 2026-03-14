# models.py

from django.db import models
from django.contrib.postgres.fields import JSONField  # для PostgreSQL
from django.core.validators import MinValueValidator, MaxValueValidator
import os
from django.utils import timezone

class District(models.Model):
    """
    Модель района с географическими координатами
    """
    name = models.CharField('Название района', max_length=100)
        
    # Координаты центра района для отображения на карте
    center_latitude = models.DecimalField(
        'Широта центра', 
        max_digits=10, 
        decimal_places=8,
        help_text='Например: 55.7558'
    )
    center_longitude = models.DecimalField(
        'Долгота центра', 
        max_digits=11, 
        decimal_places=8,
        help_text='Например: 37.6176'
    )
    
    # GeoJSON границ района (для точной обводки на карте)
    boundary_geojson = models.JSONField(
        'Границы района GeoJSON',
        blank=True, 
        null=True,
        help_text='GeoJSON объект с границами района'
    )
    
    # Кэшированное количество домов для быстрого отображения на карте
    houses_count = models.PositiveIntegerField(
        'Количество домов',
        default=0,
        editable=False
    )
    
    class Meta:
        verbose_name = 'Район'
        verbose_name_plural = 'Районы'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['center_latitude', 'center_longitude']),
        ]
    
    def __str__(self):
        return self.name
    
    def update_houses_count(self):
        """Обновить кэш количества домов"""
        self.houses_count = self.houses.count()
        self.save(update_fields=['houses_count'])


class House(models.Model):
    """
    Модель дома в портфолио
    """
    HOUSE_STATUS = [
        ('built', 'Построен'),
        ('in_progress', 'Строится'),
        ('planning', 'В планах'),
    ]
    
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='houses',
        verbose_name='Район'
    )
    
    # Основная информация
    name = models.CharField('Название дома', max_length=200)
    description = models.TextField('Описание', blank=True)
    address = models.CharField('Адрес', max_length=300, blank=True)
    
    # Характеристики дома
    built_year = models.PositiveIntegerField(
        'Год постройки',
        null=True,
        blank=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    area_sqm = models.DecimalField(
        'Площадь (м²)',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    floors = models.PositiveSmallIntegerField(
        'Количество этажей',
        null=True,
        blank=True
    )
    price = models.DecimalField(
        'Цена',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Цена в рублях'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=HOUSE_STATUS,
        default='built'
    )
    
    # Дополнительные характеристики (можно хранить в JSON)
    features = models.JSONField(
        'Дополнительные характеристики',
        blank=True,
        default=dict,
        help_text='Например: {"material": "кирпич", "parking": true}'
    )
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Дом'
        verbose_name_plural = 'Дома'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['district', 'status']),
            
        ]
    
    def __str__(self):
        return f"{self.name} ({self.district.name})"
    
    def save(self, *args, **kwargs):
        """При сохранении обновляем кэш в районе"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Обновляем счетчик домов в районе
        if is_new or self.district_id:
            self.district.update_houses_count()


def house_media_path(instance, filename):
    """Генерация пути для загрузки медиафайлов дома"""
    return f'houses/{instance.house.id}/{filename}'


class HouseMedia(models.Model):
    """
    Медиафайлы дома (фото, видео, 3D-туры)
    """
    MEDIA_TYPES = [
        ('image', 'Изображение'),
        ('video', 'Видео'),
    ]
    
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name='Дом'
    )
    
    media_type = models.CharField(
        'Тип медиа',
        max_length=20,
        choices=MEDIA_TYPES,
        default='image'
    )
    
    # Файл
    file = models.FileField(
        'Файл',
        upload_to=house_media_path,
        max_length=500
    )
    
    # Для видео можно храть ссылку на YouTube/Vimeo
    video_url = models.URLField(
        'Ссылка на видео',
        blank=True,
        help_text='Для видео можно указать внешнюю ссылку'
    )
    
    title = models.CharField('Название', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True)
    
    # Порядок сортировки
    order = models.PositiveIntegerField('Порядок', default=0)
    
    # Является ли главным изображением
    is_primary = models.BooleanField('Главное фото', default=False)
    
    created_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Медиафайл дома'
        verbose_name_plural = 'Медиафайлы домов'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.get_media_type_display()} для {self.house.name}"
    
    def save(self, *args, **kwargs):
        # Если это главное фото, сбрасываем флаг у других медиа этого дома
        if self.is_primary:
            HouseMedia.objects.filter(house=self.house, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ''


class Review(models.Model):
    """
    Модель отзыва, привязанного к дому
    """
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Дом'
    )
    
    # Информация об авторе
    author_name = models.CharField('Имя автора', max_length=100)
        
    # Отзыв
    rating = models.PositiveSmallIntegerField(
        'Оценка',
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField('Текст отзыва')
    
    # Модерация
    is_moderated = models.BooleanField('Промодерировано', default=False)
    is_published = models.BooleanField('Опубликовано', default=True)
    
    # Медиафайлы к отзыву (фото дома от клиента)
    photos = models.ManyToManyField(
        HouseMedia,
        blank=True,
        verbose_name='Фото к отзыву',
        help_text='Можно прикрепить фото из медиатеки дома'
    )
    
    # Ответ от застройщика
    response_text = models.TextField('Ответ компании', blank=True)
    response_date = models.DateTimeField('Дата ответа', null=True, blank=True)
    
    created_at = models.DateTimeField('Дата отзыва', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['house', '-created_at']),
            models.Index(fields=['rating', 'is_published']),
        ]
    
    def __str__(self):
        return f"Отзыв от {self.author_name} на {self.house.name}"
    
    def save(self, *args, **kwargs):
        # Если есть ответ, автоматически проставляем дату ответа
        if self.response_text and not self.response_date:
            self.response_date = timezone.now()
        super().save(*args, **kwargs)