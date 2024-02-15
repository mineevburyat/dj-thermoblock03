from enum import unique
from django.db import models
from django.forms import CharField
from django.urls import reverse

# Create your models here.
# TODO product link with certificats and instructions

DENSITY_CONCRETE = 2400


class Products(models.Model):
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ("pk",)
    slug = models.SlugField(unique=True)
    title = models.CharField(verbose_name='Название продукта',
                            max_length=25,
                            help_text='Артикул',
                            unique=True)
    subtitle = models.CharField(verbose_name='Подзаголовок продукта',
                            max_length=105,
                            help_text='')
    length = models.IntegerField(verbose_name='Длинна блока',
                            help_text='(мм.)')
    width = models.IntegerField(verbose_name='Ширина блока',
                            help_text='(мм.)')
    height = models.IntegerField(verbose_name='Высота блока',
                            help_text='(мм.)')
    block_weight = models.IntegerField(verbose_name='Вес блока',
                            help_text='(кг.)')
    blocks_in_paddon = models.IntegerField(verbose_name='Блоков в паддоне',
                            help_text='(шт.)')
    soundproofing = models.DecimalField(verbose_name='Звукоизоляция',
                                        max_digits=4,
                                        decimal_places=2,
                                        help_text='(Дб)')
    concrete = models.DecimalField(verbose_name='расход бетона',
                                   max_digits=4,
                                        decimal_places=3,
                                        help_text='(м.куб./м.кв.)')
    block_consumption = models.DecimalField(verbose_name='Расход блоков',
                                        max_digits=4,
                                        decimal_places=2,
                                        help_text='(шт./м.кв.)')
    images = models.ImageField(verbose_name='Изображение',
                               upload_to='img_products')
    
    def paddon_weight(self):
        value = round(self.block_weight * self.blocks_in_paddon, 2)
        return (value, 'кг.')
    
    def wall_weight(self):
        value = self.block_weight * self.block_consumption + self.concrete * DENSITY_CONCRETE
        return (round(value,2), 'кг./м.кв.')
    
    def __str__(self):
        return f"{self.title} ({self.length}x{self.width}x{self.height})"

    def img_alt(self):
        return f"{self.title} {self.subtitle}"
    
    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"product_slug": self.slug})
    
    def get_characteristics(self):
        return Characteristics.objects.filter(product=self)
    
    def get_dimensions(self):
        return f"{self.length // 10}/{self.width // 10}/{self.height // 10}"
    
class Characteristics(models.Model):
    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
    name = models.CharField(verbose_name='Название параметра',
                            max_length=35)
    value = models.DecimalField(verbose_name='Значение',
                                        max_digits=5,
                                        decimal_places=2)
    unit =  models.CharField(verbose_name='Единица измерения',
                            max_length=10)
    product = models.ForeignKey(Products,
                                verbose_name='продукт',
                                on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} {self.value} {self.unit} ({self.product.title})"
    
    
class MediaProduct(models.Model):
    class Meta:
        verbose_name = "Медиаресурс"
        verbose_name_plural = "Медиаресурсы"
    image = models.ImageField(verbose_name='Изображение',
                              upload_to='img_products',
                              blank=True,
                              null=True)
    youtube_url = models.URLField(verbose_name='Ссылка на видео',
                                  blank=True,
                                null=True)
    product = models.ForeignKey(Products,
                                verbose_name='продукт',
                                on_delete=models.CASCADE)
    
