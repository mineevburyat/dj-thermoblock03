from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils.text import slugify
from sorl.thumbnail import ImageField
import os

class MediaLibrary(models.Model):
    """
    Медиабиблиотека для хранения всех типов файлов
    """
    MEDIA_TYPES = (
        ('image', 'Изображение'),
        ('video_file', 'Видеофайл'),
        ('video_link', 'Ссылка на видео'),
        ('document', 'Документ'),
        ('drawing', 'Чертеж'),
        ('other', 'Другое'),
    )
    
    # Разрешенные расширения для разных типов
    VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
    DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt']
    DRAWING_EXTENSIONS = ['dwg', 'dxf', 'cdw', 'step', 'stp', 'iges', 'igs']
    IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
    
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    media_type = models.CharField('Тип медиа', max_length=20, choices=MEDIA_TYPES, default='image')
    
    # Поля для разных типов контента
    image = ImageField(
        'Изображение', 
        upload_to='blockproducts/images/',
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(IMAGE_EXTENSIONS)]
    )
    
    video_file = models.FileField(
        'Видеофайл',
        upload_to='blockproducts/videos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(VIDEO_EXTENSIONS)]
    )
    
    video_link = models.URLField('Ссылка на видео', blank=True)
    
    document = models.FileField(
        'Документ',
        upload_to='blockproducts/documents/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(DOCUMENT_EXTENSIONS)]
    )
    
    drawing = models.FileField(
        'Чертеж',
        upload_to='blockproducts/drawings/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(DRAWING_EXTENSIONS)]
    )
    
    other_file = models.FileField(
        'Другой файл',
        upload_to='blockproducts/other/',
        blank=True,
        null=True
    )
    
    # Общие поля
    alt_text = models.CharField('Alt текст', max_length=200, blank=True, 
                               help_text='Для изображений')
    order = models.PositiveIntegerField('Порядок', default=0)
    file_size = models.PositiveIntegerField('Размер файла (байт)', editable=False, null=True)
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    
    # Связи (может быть привязано либо к блоку, либо к серии)
    block = models.ForeignKey(
        'Block',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_media',
        verbose_name='Блок'
    )
    
    series = models.ForeignKey(
        'BlockSeries',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_media',
        verbose_name='Серия'
    )
    
    class Meta:
        verbose_name = 'Медиафайл'
        verbose_name_plural = 'Медиабиблиотека'
        ordering = ['order', '-uploaded_at']
        indexes = [
            models.Index(fields=['media_type']),
            models.Index(fields=['block']),
            models.Index(fields=['series']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Автоматическое определение типа по расширению файла
        if not self.media_type or self.media_type == 'other':
            self.detect_media_type()
        
        # Определяем размер файла
        self.update_file_size()
        
        # Alt текст для изображений
        if not self.alt_text and self.title and self.media_type == 'image':
            self.alt_text = self.title
        
        # Проверяем, что файл привязан только к одному объекту
        if self.block and self.series:
            raise ValueError('Медиафайл может быть привязан либо к блоку, либо к серии, но не к обоим сразу')
        
        super().save(*args, **kwargs)
    
    def detect_media_type(self):
        """Определяет тип медиа по расширению файла"""
        # Проверяем image
        if self.image:
            self.media_type = 'image'
            return
        
        # Проверяем video_file
        if self.video_file:
            ext = os.path.splitext(self.video_file.name)[1][1:].lower()
            if ext in self.VIDEO_EXTENSIONS:
                self.media_type = 'video_file'
            return
        
        # Проверяем document
        if self.document:
            ext = os.path.splitext(self.document.name)[1][1:].lower()
            if ext in self.DOCUMENT_EXTENSIONS:
                self.media_type = 'document'
            return
        
        # Проверяем drawing
        if self.drawing:
            ext = os.path.splitext(self.drawing.name)[1][1:].lower()
            if ext in self.DRAWING_EXTENSIONS:
                self.media_type = 'drawing'
            return
        
        # Проверяем other_file
        if self.other_file:
            self.media_type = 'other'
            return
        
        # Проверяем video_link
        if self.video_link:
            self.media_type = 'video_link'
            return
    
    def update_file_size(self):
        """Обновляет размер файла"""
        for field in ['image', 'video_file', 'document', 'drawing', 'other_file']:
            file_field = getattr(self, field)
            if file_field and hasattr(file_field, 'size'):
                self.file_size = file_field.size
                break
    
    @property
    def file_url(self):
        """Возвращает URL файла в зависимости от типа"""
        if self.image:
            return self.image.url
        elif self.video_file:
            return self.video_file.url
        elif self.document:
            return self.document.url
        elif self.drawing:
            return self.drawing.url
        elif self.other_file:
            return self.other_file.url
        elif self.video_link:
            return self.video_link
        return ''
    
    @property
    def file_extension(self):
        """Возвращает расширение файла"""
        for field in ['image', 'video_file', 'document', 'drawing', 'other_file']:
            file_field = getattr(self, field)
            if file_field:
                return os.path.splitext(file_field.name)[1][1:].lower()
        return ''
    
    @property
    def filename(self):
        """Возвращает имя файла"""
        for field in ['image', 'video_file', 'document', 'drawing', 'other_file']:
            file_field = getattr(self, field)
            if file_field:
                return os.path.basename(file_field.name)
        return ''
    
    def get_icon(self):
        """Возвращает иконку для типа файла"""
        icons = {
            'image': '🖼️',
            'video_file': '🎬',
            'video_link': '🔗',
            'document': '📄',
            'drawing': '📐',
            'other': '📁',
        }
        return icons.get(self.media_type, '📄')
    
    def get_thumbnail(self, geometry='100x100'):
        """Получить миниатюру для изображений"""
        if self.media_type == 'image' and self.image:
            from sorl.thumbnail import get_thumbnail
            try:
                return get_thumbnail(self.image, geometry, crop='center')
            except:
                return None
        return None


class BlockSeries(models.Model):
    """
    Серия блоков
    """
    SERIES_TYPES = (
        ('monolithic', 'Монолитная'),
        ('block', 'Блочная'),
    )
    
    name = models.CharField('Название серии', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=120, unique=True, blank=True)
    series_type = models.CharField('Тип', max_length=20, choices=SERIES_TYPES)
    description = models.TextField('Описание', blank=True)
    order = models.SmallIntegerField('Порядок', default=10)
    # Главное изображение серии
    main_image = models.ForeignKey(
        MediaLibrary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='series_main_image',
        verbose_name='Главное фото',
        limit_choices_to={'media_type': 'image'}
    )
    
    # Дополнительные фото/видео
    additional_media = models.ManyToManyField(
        MediaLibrary,
        blank=True,
        related_name='series_media',
        verbose_name='Дополнительные медиа'
    )
    
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Серия блоков'
        verbose_name_plural = 'Серии блоков'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_series_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CharacteristicGroup(models.Model):
    """
    Группа характеристик для серии
    """
    series = models.ForeignKey(
        BlockSeries,
        on_delete=models.CASCADE,
        related_name='characteristic_groups',
        verbose_name='Серия'
    )
    name = models.CharField('Название группы', max_length=100)
    
    # Характеристики группы
    wall_thickness = models.DecimalField('Толщина стены (мм)', max_digits=6, decimal_places=2)
    thermal_conductivity = models.DecimalField('Теплопроводность', max_digits=5, decimal_places=3, blank=True, null=True)
    sound_insulation = models.DecimalField('Звукоизоляция (дБ)', max_digits=5, decimal_places=2, blank=True, null=True)
    concrete_consumption = models.DecimalField('Расход бетона (м³/м²)', max_digits=6, decimal_places=4, blank=True, null=True)
    weight_per_sqm = models.DecimalField('Вес 1 м² стены (кг)', max_digits=7, decimal_places=2)
    
    class Meta:
        verbose_name = 'Группа характеристик'
        verbose_name_plural = 'Группы характеристик'
        unique_together = ['series', 'wall_thickness']  # Одна толщина на серию
        ordering = ['series', 'wall_thickness']
    
    def __str__(self):
        return f"{self.series.name} - {self.wall_thickness}мм"
    
    def save(self, *args, **kwargs):
        # Проверяем, что у серии не больше двух групп
        if not self.pk:  # Только для новых записей
            if self.series.characteristic_groups.count() >= 2:
                raise ValueError('У серии может быть не больше двух групп характеристик')
        super().save(*args, **kwargs)


class Block(models.Model):
    """
    Блок
    """
    BLOCK_TYPES = (
        ('corner', 'Угловой'),
        ('inline', 'Рядный'),
        ('inline_extended', 'Рядный удлиненный'),
        ('other', 'Другой'),
    )
    
    series = models.ForeignKey(
        BlockSeries,
        on_delete=models.CASCADE,
        related_name='blocks',
        verbose_name='Серия'
    )
    
    # Опционально: привязка к группе характеристик (толщине)
    characteristic_group = models.ForeignKey(
        CharacteristicGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocks',
        verbose_name='Группа характеристик'
    )
    
    block_type = models.CharField('Тип блока', max_length=20, choices=BLOCK_TYPES)
    article = models.CharField('Артикул', max_length=50, unique=True)
    name = models.CharField('Название', max_length=200)
    
    # Габариты
    length = models.DecimalField('Длина (мм)', max_digits=6, decimal_places=2)
    width = models.DecimalField('Ширина (мм)', max_digits=6, decimal_places=2)
    height = models.DecimalField('Высота (мм)', max_digits=6, decimal_places=2)
    
    # Вес и упаковка
    weight = models.DecimalField('Вес блока (кг)', max_digits=7, decimal_places=2)
    pallet_quantity = models.PositiveIntegerField('Количество на поддоне')
    
    # Главное изображение блока
    main_image = models.ForeignKey(
        MediaLibrary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='block_main_image',
        verbose_name='Главное фото'
    )
    
    # Дополнительные медиа для блока
    additional_media = models.ManyToManyField(
        MediaLibrary,
        blank=True,
        related_name='block_media',
        verbose_name='Дополнительные медиа'
    )
    
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'
        ordering = ['series', 'block_type']
        unique_together = ['series', 'block_type', 'characteristic_group']
    
    def __str__(self):
        name = f"{self.series.name} - {self.get_block_type_display()}"
        if self.characteristic_group:
            name += f" ({self.characteristic_group.wall_thickness}мм)"
        return name
    
    @property
    def pallet_weight(self):
        """Вес поддона"""
        return self.weight * self.pallet_quantity
    
    @property
    def blocks_per_sqm(self):
        """Количество блоков на 1 м² стены"""
        if self.height > 0:
            return round(1_000_000 / (self.length * self.height), 2)
        return 0