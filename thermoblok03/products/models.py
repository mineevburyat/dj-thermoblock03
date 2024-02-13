from turtle import width
from django.db import models
from django.forms import CharField

# Create your models here.
# TODO models for products

DENSITY_CONCRETE = 2300


class Products(models.Model):
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

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
        value = self.block_weight * self.blocks_in_paddon
        return (value, 'кг.')
    
    def wall_weight(self):
        value = self.block_weight * self.block_consumption + self.concrete * DENSITY_CONCRETE
        return (value, 'кг./м.кв.')
    
    def __str__(self):
        return f"{self.title} ({self.length}x{self.width}x{self.height})"

    def img_alt(self):
        return f"{self.title} {self.subtitle}"
    
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
    
