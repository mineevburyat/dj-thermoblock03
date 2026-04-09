# admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import District, House, HouseMedia, Review

class HouseMediaInline(admin.TabularInline):
    model = HouseMedia
    extra = 1
    fields = ['media_type', 'file', 'video_url', 'title', 'is_primary',]


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ['author_name', 'rating', 'text', 'is_published']
    readonly_fields = ['created_at']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'houses_count', ]
    search_fields = ['name']
    readonly_fields = ['houses_count',]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', )
        }),
        ('Координаты', {
            'fields': ('center_latitude', 'center_longitude', 'boundary_geojson')
        }),
        ('Системное', {
            'fields': ('houses_count', ),
            'classes': ('collapse',)
        }),
    )


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'status', 'display_primary_image']
    list_filter = ['district', 'status', 'built_year']
    search_fields = ['name', ]
    # inlines = [HouseMediaInline, ReviewInline]
    readonly_fields = ['created_at', 'updated_at']
    
    # def display_primary_image(self, obj):
    #     primary = obj.media.filter(is_primary=True).first()
    #     if primary and primary.file:
    #         return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', 
    #                          primary.file.url)
    #     return 'Нет фото'
    def display_primary_image(self, obj):
        primary = obj.photo
        print(primary, dir(primary))
        if primary and primary.file:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', 
                             primary.url)
        return 'Нет фото'
    display_primary_image.short_description = 'Главное фото'


@admin.register(HouseMedia)
class HouseMediaAdmin(admin.ModelAdmin):
    list_display = ['house', 'media_type', 'title', 'is_primary', ]
    list_filter = ['media_type', 'is_primary']
    search_fields = ['house__name', 'title']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'house', 'rating', 'is_published', 'created_at']
    list_filter = ['rating', 'is_published', 'house__district']
    search_fields = ['author_name', 'text']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Отзыв', {
            'fields': ('house', 'author_name', 'rating', 'text')
        }),
        ('Медиа', {
            'fields': ('photos',)
        }),
        ('Модерация', {
            'fields': ('is_moderated', 'is_published')
        }),
        ('Ответ компании', {
            'fields': ('response_text', 'response_date')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )