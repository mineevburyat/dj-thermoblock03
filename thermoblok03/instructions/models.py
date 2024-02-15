from os import uname
from pyexpat import model
from django.db import models

# Create your models here.
# TODO model with instructions

MEDIA_TYPE = [
    ("image", "Изображение"),
    ("video", "Видео"),
    ("url", "Ссылка"),
    ("file", "Файл")
]

class Instractions(models.Model):
    class Meta:
        verbose_name = 'Инструкцию'
        verbose_name_plural = 'Инструкции'

    name = models.CharField(verbose_name='название инструкции',
                            max_length=35,
                            blank=True,
                            null=True)
    description = models.TextField(verbose_name='краткое описание инструкции')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    

class StageInstruction(models.Model):
    class Meta:
        verbose_name = 'Этап'
        verbose_name_plural = 'Этапы'

    page = models.PositiveIntegerField()
    title = models.CharField(verbose_name='название этапа',
                            max_length=35)
    description = models.TextField(verbose_name='краткое описание этапа')
    instruction = models.ForeignKey(Instractions,
                                    verbose_name='инструкция')
    
    def __str__(self):
        return f"{self.instruction.name} {self.title} ({self.page})"
    

class StageRecomendation(models.Model):
    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'

    tab_name = models.CharField(verbose_name='название рекомендации',
                            max_length=25)
    type_media = models.CharField(verbose_name='название этапа',
                            max_length=6,
                            choices=MEDIA_TYPE,
                            default='image')
    image = models.ImageField(verbose_name='изображение',
                              )