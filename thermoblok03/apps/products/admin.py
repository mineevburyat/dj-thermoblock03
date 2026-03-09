from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.urls import reverse
from .models import MediaLibrary, BlockSeries, CharacteristicGroup, Block

class BaseAdmin(admin.ModelAdmin):
    """Базовый класс с вспомогательными методами для URL"""
    
    def get_admin_url(self, obj, action='change'):
        """Получить URL для объекта в админке"""
        if not obj or not obj.pk:
            return '#'
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        return reverse(f'admin:{app_label}_{model_name}_{action}', args=[obj.pk])
    
    def get_changelist_url(self, model_class):
        """Получить URL для списка объектов"""
        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name
        return reverse(f'admin:{app_label}_{model_name}_changelist')

class BlockSeriesForm(forms.ModelForm):
    """Форма для серии с проверкой количества групп"""
    
    class Meta:
        model = BlockSeries
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        # Дополнительные проверки можно добавить здесь
        return cleaned_data


class CharacteristicGroupInline(admin.TabularInline):
    """Инлайн для групп характеристик"""
    model = CharacteristicGroup
    extra = 0
    max_num = 2  # Максимум 2 группы
    fields = ['name', 'wall_thickness', 'weight_per_sqm', 
              'thermal_conductivity', 'sound_insulation', 'concrete_consumption']
    
    def get_extra(self, request, obj=None, **kwargs):
        """Показываем только если можно добавить еще группу"""
        if obj and obj.characteristic_groups.count() >= 2:
            return 0
        return 1


class BlockInline(admin.TabularInline):
    """Инлайн для блоков"""
    model = Block
    extra = 0
    fields = ['block_type', 'article', 'name', 'length', 'width', 'height',
              'weight', 'pallet_quantity', 'preview_link']
    readonly_fields = ['preview_link']
    
    def preview_link(self, obj):
        if obj.pk:
            return format_html('<a href="{}">✏️ Ред.</a>', 
                             f'/admin/app/block/{obj.pk}/change/')
        return '—'
    preview_link.short_description = ''
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('characteristic_group')



class MediaLibraryForm(forms.ModelForm):
    """Форма для медиабиблиотеки с валидацией"""
    
    class Meta:
        model = MediaLibrary
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        block = cleaned_data.get('block')
        series = cleaned_data.get('series')
        
        # Проверка на привязку только к одному объекту
        if block and series:
            raise forms.ValidationError('Медиафайл может быть привязан либо к блоку, либо к серии, но не к обоим сразу')
        
        # Проверка на заполнение хотя бы одного поля с контентом
        content_fields = ['image', 'video_file', 'video_link', 'document', 'drawing', 'other_file']
        has_content = any(cleaned_data.get(field) for field in content_fields)
        
        if not has_content:
            raise forms.ValidationError('Заполните хотя бы одно поле с контентом')
        
        return cleaned_data


@admin.register(MediaLibrary)
class MediaLibraryAdmin(BaseAdmin):
    form = MediaLibraryForm
    list_display = ['preview', 'title', 'media_type', 'file_info', 
                   'linked_to', 'order', 'uploaded_at']
    list_display_links = ['preview', 'title']
    list_filter = ['media_type', 'uploaded_at']
    search_fields = ['title', 'description', 'alt_text']
    list_editable = ['order']
    list_per_page = 25
    autocomplete_fields = ['block', 'series']
    
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'description', 'media_type', 'alt_text')
        }),
        ('Контент', {
            'fields': (
                'image', 'video_file', 'video_link', 
                'document', 'drawing', 'other_file'
            ),
            'description': 'Заполните одно из полей в зависимости от типа медиа'
        }),
        ('Привязка', {
            'fields': ('block', 'series'),
            'description': 'Привяжите либо к блоку, либо к серии'
        }),
        ('Настройки', {
            'fields': ('order',),
            'classes': ('wide',)
        }),
    )
    
    readonly_fields = ['file_size', 'preview_detail']
    
    def preview(self, obj):
        if obj.media_type == 'image' and obj.image:
            thumb = obj.get_thumbnail('50x50')
            if thumb:
                return format_html('<img src="{}" style="border-radius: 4px;">', thumb.url)
            return '🖼️'
        return obj.get_icon()
    preview.short_description = ''
    
    def file_info(self, obj):
        info = obj.file_extension.upper() if obj.file_extension else ''
        if obj.file_size:
            size_mb = obj.file_size / (1024 * 1024)
            info += f' ({size_mb:.1f} МБ)'
        return info or '—'
    file_info.short_description = 'Файл'
    
    def linked_to(self, obj):
        if obj.block:
            url = self.get_admin_url(obj.block)
            return format_html('Блок: <a href="{}">{}</a>', url, obj.block.name)
        elif obj.series:
            url = self.get_admin_url(obj.series)
            return format_html('Серия: <a href="{}">{}</a>', url, obj.series.name)
        return '—'
    linked_to.short_description = 'Привязка'
    
    def preview_detail(self, obj):
        if obj.media_type == 'image' and obj.image:
            thumb = obj.get_thumbnail('300x200')
            if thumb:
                return format_html('<img src="{}" style="max-width: 300px;">', thumb.url)
        elif obj.video_link:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.video_link, obj.video_link)
        elif obj.video_file:
            return format_html('<video width="300" controls><source src="{}" type="video/mp4"></video>', 
                             obj.video_file.url)
        return 'Нет предпросмотра'
    preview_detail.short_description = 'Предпросмотр'
    
    actions = ['attach_to_block', 'attach_to_series', 'remove_attachment']
    
    def attach_to_block(self, request, queryset):
        block_id = request.POST.get('block_id')
        if block_id:
            queryset.update(block_id=block_id, series=None)
            self.message_user(request, f'Прикреплено к блоку: {queryset.count()}')
    attach_to_block.short_description = 'Прикрепить к блоку'
    
    def attach_to_series(self, request, queryset):
        series_id = request.POST.get('series_id')
        if series_id:
            queryset.update(series_id=series_id, block=None)
            self.message_user(request, f'Прикреплено к серии: {queryset.count()}')
    attach_to_series.short_description = 'Прикрепить к серии'
    
    def remove_attachment(self, request, queryset):
        queryset.update(block=None, series=None)
        self.message_user(request, f'Откреплено: {queryset.count()}')
    remove_attachment.short_description = 'Убрать привязку'


@admin.register(BlockSeries)
class BlockSeriesAdmin(BaseAdmin):
    list_display = ['name', 'series_type', 'groups_count', 'blocks_count', 
                   'media_count', 'is_active']
    list_filter = ['series_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug', 'series_type', 'description')
        }),
        ('Медиа', {
            'fields': ('main_image',),
            'description': 'Главное изображение серии. Дополнительные медиа добавляются через медиабиблиотеку'
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )
    
    inlines = [CharacteristicGroupInline, BlockInline]

    def groups_count(self, obj):
        count = obj.characteristic_groups.count()
        return format_html('{} / 2', count)
    groups_count.short_description = 'Группы'
    
    def blocks_count(self, obj):
        count = obj.blocks.count()
        url = self.get_changelist_url(Block) + f'?series__id__exact={obj.pk}'
        return format_html('<a href="{}">{}</a>', url, count)
    blocks_count.short_description = 'Блоки'
    
    def media_count(self, obj):
        count = obj.linked_media.count()
        url = self.get_changelist_url(MediaLibrary) + f'?series__id__exact={obj.pk}'
        return format_html('<a href="{}">{} 📎</a>', url, count)
    media_count.short_description = 'Медиа'


@admin.register(CharacteristicGroup)
class CharacteristicGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'series', 'wall_thickness', 'weight_per_sqm', 
                   'thermal_conductivity', 'sound_insulation']
    list_filter = ['series']
    search_fields = ['series__name']
    autocomplete_fields = ['series']


@admin.register(Block)
class BlockAdmin(BaseAdmin):
    list_display = ['article', 'name', 'series', 'block_type', 
                   'dimensions', 'weight', 
                   'pallet_info', 'media_count', 'pallet_weight_display', 'is_active']
    list_filter = ['series', 'block_type', 'is_active']
    search_fields = ['article', 'name']
    list_editable = ['is_active']
    autocomplete_fields = ['series', 'characteristic_group']
    readonly_fields = ['pallet_weight_display', 'blocks_per_sqm_display']

    fieldsets = (
        ('Основное', {
            'fields': ('series', 'characteristic_group', 'block_type', 
                      'article', 'name')
        }),
        ('Габариты', {
            'fields': ('length', 'width', 'height')
        }),
        ('Вес и упаковка', {
            'fields': ('weight', 'pallet_quantity', 'pallet_weight_display')
        }),
        ('Медиа', {
            'fields': ('main_image',),
            'description': 'Главное изображение блока. Дополнительные медиа добавляются через медиабиблиотеку'
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )
    
    # def thickness_display(self, obj):
    #     if obj.characteristic_group:
    #         return f"{obj.characteristic_group.wall_thickness}мм"
    #     return '—'
    # thickness_display.short_description = 'Толщина'
    
    def dimensions(self, obj):
        return f"{obj.length}×{obj.width}×{obj.height}"
    dimensions.short_description = 'Габариты (мм)'
    
    def pallet_info(self, obj):
        return f"{obj.pallet_quantity} шт ({obj.pallet_weight} кг)"
    pallet_info.short_description = 'Поддон'
    
    def series_link(self, obj):
        url = self.get_admin_url(obj.series)
        return format_html('<a href="{}">{}</a>', url, obj.series.name)
    series_link.short_description = 'Серия'
    series_link.admin_order_field = 'series__name'
    
    def media_count(self, obj):
        count = obj.linked_media.count()
        url = self.get_changelist_url(MediaLibrary) + f'?block__id__exact={obj.pk}'
        if count:
            return format_html('<a href="{}">{} 📎</a>', url, count)
        return '—'
    media_count.short_description = 'Медиа'
    
    def pallet_weight_display(self, obj):
        return f"{obj.pallet_weight} кг"
    pallet_weight_display.short_description = 'Вес поддона'
    
    def blocks_per_sqm_display(self, obj):
        return f"{obj.blocks_per_sqm} шт/м²"
    blocks_per_sqm_display.short_description = 'Расход на м²'