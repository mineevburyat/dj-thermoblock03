from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class ProductType(models.Model):
    """Тип строения (категория)"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', max_length=120, unique=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    FLOOR_CHOICES = [
        (1.0, '1'),
        (1.5, '1.5'),
        (2.0, '2'),
        (3.0, '3'),
        (0.0, '0'),
    ]
    floor = models.DecimalField(
        max_digits=2, 
        decimal_places=1, 
        choices=FLOOR_CHOICES,
        default=0.0,
        verbose_name="Этажность"
    )
    class Meta:
        verbose_name = 'Тип строения'
        verbose_name_plural = 'Типы строений'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_first_project_image(self):
        """
        Возвращает первое изображение из первого активного проекта этой категории.
        Используется для отображения карточек категорий на главной странице.
        """
        # Получаем первый активный проект в этой категории
        first_project = self.products.filter(is_active=True).first()
        
        if first_project:
            # Возвращаем главное изображение проекта или первое попавшееся
            return first_project.get_first_image()
        return None
    
    def get_image_url(self):
        """
        Возвращает URL изображения для категории.
        Сначала проверяет, есть ли у категории собственное изображение,
        если нет - берет из первого проекта.
        """
        
        first_image = self.get_first_project_image()
        if first_image and first_image.image:
            return first_image.image.url
        return None
    
    def get_floor_count(self):
        return self.get_floor_display()

class RoofType(models.Model):
    """Тип крыши"""
    name = models.CharField('Название', max_length=50)
    slug = models.SlugField('URL', max_length=60, unique=True)
    
    class Meta:
        verbose_name = 'Тип крыши'
        verbose_name_plural = 'Типы крыш'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    """Модель проекта дома"""
        # Основные поля
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=250, unique=True, db_index=True)
    article = models.CharField('Артикул', max_length=50, blank=True, db_index=True)
    order = models.PositiveIntegerField('Порядок', default=1000)
    # Связи
    product_type = models.ForeignKey(
        ProductType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Тип строения',
        related_name='products'
    )
    roof_type = models.ForeignKey(
        RoofType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Тип крыши',
        related_name='products'
    )
    
    # Характеристики
    area = models.DecimalField(
        'Площадь, м²', 
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    rooms_count = models.PositiveSmallIntegerField(
        'Количество комнат', 
        null=True, 
        blank=True,
        validators=[MinValueValidator(1)]
    )
    bathrooms_count = models.PositiveSmallIntegerField(
        'Количество санузлов', 
        null=True, 
        blank=True
    )
        
    # Дополнительные характеристики (опционально)
    bedrooms_count = models.PositiveSmallIntegerField(
        'Количество спален', 
        null=True, 
        blank=True
    )
    garage = models.BooleanField('Гараж', default=False)
    terrace = models.BooleanField('Терраса', default=False)
    
    # Описание
    description = models.TextField('Описание', blank=True)
    short_description = models.CharField('Краткое описание', max_length=500, blank=True)
    
    # Мета-данные
    is_active = models.BooleanField('Активно', default=True)
    is_popular = models.BooleanField('Популярное', default=False)
    is_new = models.BooleanField('Новинка', default=False)
    
    # SEO
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    meta_keywords = models.CharField('Meta Keywords', max_length=300, blank=True)
    
    # Даты
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Проект строения'
        verbose_name_plural = 'Проекты строений'
        ordering = ['title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['product_type']),
            models.Index(fields=['is_active']),
        ]
    
    def floors_count(self):
        'Количество этажей'
        if self.product_type:
            return self.product_type.get_floor_count()
        else:
            return '-'

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_first_image(self):
        """Возвращает первое изображение для использования в шаблонах"""
        first = self.images.filter(is_main=True).order_by('order').first()
        if not first:
            first = self.images.first()
        return first
    



class ProductImage(models.Model):
    """Модель для хранения изображений проектов"""
    class ImageType(models.TextChoices):
        FACADE = ('facade', 'Фасад')
        PLAN = ('plan', 'Планировка')
        INTERIOR = ('interior', 'Интерьер')
        EXTERIOR = ('exterior', 'Екстерьер')
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Проект'
    )
    image = models.ImageField(
        'Изображение', 
        upload_to='constructs/'
    )
    image_type = models.CharField(
        max_length=20, 
        choices=ImageType.choices, 
        default=ImageType.EXTERIOR, 
        verbose_name='Тип изображения'
    )
    alt = models.CharField(
        'Alt текст', 
        max_length=120, 
        blank=True,
        help_text='только вид, перед этим будет добавдено название проекта и вид фотографии')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_main = models.BooleanField('Главное', default=False)
    
    class Meta:
        verbose_name = 'Изображение проекта'
        verbose_name_plural = 'Изображения проектов'
        ordering = ['order']
    
    def get_alt(self):
        return f"{self.order}. {self.product.title} {self.get_image_type_display()} {self.alt}"
    
    def save(self, *args, **kwargs):
        # Если это главное изображение, сбрасываем флаг у других
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        
        # Генерируем alt если не указан
        if not self.alt and self.product:
            self.alt = f"{self.product.title} - фото {self.order}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_alt()}"