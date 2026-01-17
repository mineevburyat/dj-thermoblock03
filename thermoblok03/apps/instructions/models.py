from django.db import models
from django.urls import reverse
from .validators import validate_is_video
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
    
    def get_stages(self):
        return self.stage_set.all()
    
    def get_stages_count(self):
        return self.get_stages().count()
    
    def get_recomendations(self):
        qs = Instractions.objects.none()
        for stage in self.get_stages():
            qs = qs.union(stage.get_recomendations())
        return qs

    def get_recomendations_count(self):
        return self.get_recomendations().count()
    
    def get_absolute_url(self):
        return reverse("instructions:detail", kwargs={"pk": self.pk})
    
    

class Stage(models.Model):
    class Meta:
        verbose_name = 'Этап'
        verbose_name_plural = 'Этапы'
        unique_together = ('instruction', 'page')

    page = models.PositiveIntegerField()
    title = models.CharField(verbose_name='название этапа',
                            max_length=35)
    description = models.TextField(verbose_name='краткое описание этапа')
    instruction = models.ForeignKey(Instractions,
                                    verbose_name='инструкция',
                                    on_delete=models.PROTECT)
    
    def __str__(self):
        return f"{self.instruction.name} {self.title} ({self.page})"
    
    def get_recomendations(self):
        return self.recomendation_set.all()

class Recomendation(models.Model):
    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'
    stage = models.ForeignKey(Stage,
                              verbose_name='этап инструкции',
                              on_delete=models.PROTECT)
    tab_name = models.CharField(verbose_name='название рекомендации',
                            max_length=25)
    description = models.TextField(verbose_name='рекомендация')
    type_media = models.CharField(verbose_name='тип медиа к рекомендации',
                            max_length=6,
                            choices=MEDIA_TYPE,
                            default='image')
    image = models.ImageField(verbose_name='изображение',
                              upload_to='instractions',
                              blank=True,
                              null=True                            
                              )
    file = models.FileField(verbose_name='файл',
                              upload_to='instractions',
                              blank=True,
                              null=True                            
                              )
    video = models.FileField(verbose_name='видео',
                              upload_to='img_instractions',
                              blank=True,
                              null=True,
                              validators=(validate_is_video,)                            
                              )
    url = models.URLField(verbose_name='Ссылка на ресурс', blank=True, null=True)
    

    def __str__(self):
        return f"{str(self.stage)} {self.tab_name}"
    