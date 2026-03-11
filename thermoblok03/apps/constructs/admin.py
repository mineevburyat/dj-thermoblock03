from django.contrib import admin
from django.contrib.admin import SimpleListFilter  # Вот правильный импорт!
from django.utils.html import format_html
from django.db import models
from .models import Product, ProductImage, ProductType, RoofType



# Кастомный фильтр по наличию изображений
class HasImagesFilter(SimpleListFilter):
    title = 'наличие изображений'
    parameter_name = 'has_images'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Есть изображения'),
            ('no', 'Нет изображений'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(images__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(images__isnull=True)
        return queryset

# Кастомный фильтр по типу крыши
class RoofTypeFilter(SimpleListFilter):
    title = 'тип крыши'
    parameter_name = 'roof_type'
    
    def lookups(self, request, model_admin):
        return RoofType.objects.all().values_list('id', 'name')
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(roof_type_id=self.value())
        return queryset

# Inline для изображений
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 20
    fields = ['image_preview', 'image', 'alt', 'order', 'is_main']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 4px;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью'

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_editable = ['order']
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Товаров'
    products_count.admin_order_field = 'products__count'

@admin.register(RoofType)
class RoofTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = [
        'id',
        'order',
        'main_image_thumb', 
        'title', 
        'product_type', 
        'area_display', 
        'rooms_count', 
        'images_count',
        'is_active',
        'is_popular',
        'is_new',
        'created_at_short'
    ]
    
    list_display_links = ['id', 'main_image_thumb', 'title']
    
    # Фильтры
    list_filter = [
        'is_active',
        'is_popular',
        'is_new',
        'product_type',
        HasImagesFilter,
        RoofTypeFilter,
        'garage',
        'terrace',
        'created_at',
    ]
    
    # Поиск
    search_fields = ['title', 'article', 'description']
    
    # Редактирование в списке
    list_editable = ['order', 'is_active', 'is_popular', 'is_new']
    
    # Порядок сортировки
    ordering = ['order', '-created_at']
    
    # Количество записей на странице
    list_per_page = 25
    
    # Группировка полей в форме
    fieldsets = (
        ('Основная информация', {
            'fields': (
                ('title', 'article', 'order'),
                ('slug',),
                ('product_type', 'roof_type'),
                ('description', 'short_description'),
            ),
            'classes': ('wide',)
        }),
        ('Характеристики', {
            'fields': (
                ('area', 'floors_count'),
                ('rooms_count', 'bedrooms_count'),
                ('bathrooms_count',),
                ('garage', 'terrace'),
            ),
            'classes': ('wide', 'collapse')
        }),
        
        ('Статусы и SEO', {
            'fields': (
                ('is_active', 'is_popular', 'is_new'),
                ('meta_title', 'meta_description', 'meta_keywords'),
            ),
            'classes': ('wide', 'collapse')
        }),
        ('Даты', {
            'fields': (
                ('created_at', 'updated_at'),
            ),
            'classes': ('wide', 'collapse')
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ['created_at', 'updated_at', 'main_image_preview']
    
    # Предзаполнение slug
    prepopulated_fields = {'slug': ('title',)}
    
    # Inline изображения
    inlines = [ProductImageInline]
    
    # Действия
    actions = ['make_active', 'make_inactive', 'make_popular', 'make_new']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images', 'product_type')
    
    # Кастомные методы для отображения
    
    def main_image_thumb(self, obj):
        first_image = obj.images.filter(is_main=True).first()
        if not first_image:
            first_image = obj.images.first()
        
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px;" />',
                first_image.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #eee; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #999;">🖼️</div>')
    main_image_thumb.short_description = 'Фото'
    
    def main_image_preview(self, obj):
        """Превью главного изображения в форме редактирования"""
        first_image = obj.images.filter(is_main=True).first()
        if not first_image:
            first_image = obj.images.first()
        
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                first_image.image.url
            )
        return "Нет изображения"
    main_image_preview.short_description = 'Превью'
    
    def area_display(self, obj):
        if obj.area:
            return f"{obj.area:.1f} м²"
        return "—"
    area_display.short_description = 'Площадь'
    area_display.admin_order_field = 'area'
    
        
    def images_count(self, obj):
        count = obj.images.count()
        if count > 0:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px;">{}</span>',
                count
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 12px;">0</span>'
        )
    images_count.short_description = 'Фото'
    images_count.admin_order_field = 'images__count'
    
    def created_at_short(self, obj):
        return obj.created_at.strftime("%d.%m.%Y")
    created_at_short.short_description = 'Дата'
    created_at_short.admin_order_field = 'created_at'
    
    # Действия
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Активировано {queryset.count()} товаров")
    make_active.short_description = "Активировать выбранные товары"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {queryset.count()} товаров")
    make_inactive.short_description = "Деактивировать выбранные товары"
    
    def make_popular(self, request, queryset):
        queryset.update(is_popular=True)
        self.message_user(request, f"Отмечено популярными {queryset.count()} товаров")
    make_popular.short_description = "Отметить как популярные"
    
    def make_new(self, request, queryset):
        queryset.update(is_new=True)
        self.message_user(request, f"Отмечено новинками {queryset.count()} товаров")
    make_new.short_description = "Отметить как новинки"

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'image_thumb',
        'product_link',
        'alt_short',
        'order',
        'is_main',
        'upload_date'
    ]
    
    list_display_links = ['id', 'image_thumb']
    
    list_filter = [
        'is_main',
        'product__product_type',
        'product__is_active',
    ]
    
    search_fields = ['product__title', 'alt']
    
    list_editable = ['order', 'is_main']
    
    ordering = ['product', 'order']
    
    list_per_page = 50
    
    fieldsets = (
        ('Основное', {
            'fields': (
                'product',
                'image_preview',
                'image',
                'alt',
            )
        }),
        ('Порядок и статус', {
            'fields': (
                ('order', 'is_main'),
            )
        }),
        ('Информация о файле', {
            'fields': (
                'original_url',
                'original_filename',
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['image_preview', 'upload_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
    
    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url
            )
        return "—"
    image_thumb.short_description = 'Превью'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Просмотр'
    
    def product_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f"/admin/products/product/{obj.product.id}/change/",
            obj.product.title
        )
    product_link.short_description = 'Товар'
    product_link.admin_order_field = 'product__title'
    
    def alt_short(self, obj):
        if obj.alt:
            return obj.alt[:50] + "..." if len(obj.alt) > 50 else obj.alt
        return "—"
    alt_short.short_description = 'Alt текст'
    
    def upload_date(self, obj):
        if obj.image:
            return obj.image.name.split('/')[-1]
        return "—"
    upload_date.short_description = 'Файл'
    
    actions = ['make_main', 'make_not_main', 'regenerate_alts']
    
    def make_main(self, request, queryset):
        for image in queryset:
            image.is_main = True
            image.save()
        self.message_user(request, f"Отмечено главными {queryset.count()} изображений")
    make_main.short_description = "Сделать главными"
    
    def make_not_main(self, request, queryset):
        queryset.update(is_main=False)
        self.message_user(request, f"Убрана отметка главных с {queryset.count()} изображений")
    make_not_main.short_description = "Убрать отметку главных"
    
    def regenerate_alts(self, request, queryset):
        updated = 0
        for img in queryset:
            if img.product:
                # Находим порядковый номер
                all_images = ProductImage.objects.filter(product=img.product).order_by('order')
                for idx, product_img in enumerate(all_images, 1):
                    if product_img.id == img.id:
                        img.alt = f"{img.product.title} - фото {idx}"
                        if idx == 1:
                            img.alt = f"{img.product.title} - главное фото"
                        img.save()
                        updated += 1
                        break
        self.message_user(request, f"Обновлено alt текстов: {updated}")
    regenerate_alts.short_description = "Перегенерировать alt тексты"