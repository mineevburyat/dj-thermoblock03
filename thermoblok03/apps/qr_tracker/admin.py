# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import NoReverseMatch, reverse
from django.conf import settings
from .models import TrackedLink, ClickLog


class ClickLogInline(admin.TabularInline):
    """Инлайн для просмотра последних переходов"""
    model = ClickLog
    extra = 0
    fields = ('clicked_at', 'ip_address', 'user_agent_preview', 'referer')
    readonly_fields = fields
    max_num = 10
    can_delete = False
    
    def user_agent_preview(self, obj):
        if len(obj.user_agent) > 50:
            return obj.user_agent[:50] + '...'
        return obj.user_agent
    user_agent_preview.short_description = 'User-Agent'
    
    def get_queryset(self, request):
        """Получаем только последние 10 переходов"""
        qs = super().get_queryset(request)
        # Сначала фильтруем, потом сортируем, потом берем срез
        return qs.order_by('-clicked_at')[:10]
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TrackedLink)
class TrackedLinkAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'slug', 
        'qr_redirect_link_preview',  # Показываем ссылку для QR прямо в списке
        'target_url_preview', 
        'total_clicks', 
        'unique_clicks', 
        'qr_code_status',
        'is_active',
        'created_at'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'target_url')
    readonly_fields = (
        'total_clicks', 
        'unique_clicks', 
        'qr_redirect_link_display',  # Поле для отображения ссылки
        'qr_code_preview',
        'qr_code_instructions'
    )
    # inlines = [ClickLogInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'target_url', 'is_active')
        }),
        ('🔗 Ссылка для генерации QR-кода', {
            'fields': ('qr_redirect_link_display', 'qr_code_instructions'),
            'description': 'Скопируйте эту ссылку и вставьте в генератор QR-кодов',
            'classes': ('wide',)
        }),
        ('QR-код (загрузить готовый)', {
            'fields': ('qr_code', 'qr_code_preview'),
            'description': 'После генерации QR-кода, загрузите его сюда для хранения',
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('total_clicks', 'unique_clicks'),
            'classes': ('collapse',)
        }),
    )
    
    def qr_redirect_link_preview(self, obj):
        """Отображение ссылки для QR в списке объектов"""
        full_url = f"{settings.BASE_URL}{obj.get_absolute_url()}"
        return format_html(
            '<span style="font-family: monospace; font-size: 11px;">{}</span>',
            full_url[:50] + '...' if len(full_url) > 50 else full_url
        )
    qr_redirect_link_preview.short_description = 'Ссылка для QR'
    
    def qr_redirect_link_display(self, obj):
        """Отображение ссылки для QR с кнопкой копирования (в детальной странице)"""
        try:
            path = obj.get_absolute_url()
            full_url = f"{settings.BASE_URL}{path}"
            return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 2px solid #79aec8;">'
            '<div style="margin-bottom: 10px;">'
            '<strong style="font-size: 16px; color: #417690;">📱 Ссылка для QR-кода:</strong>'
            '</div>'
            '<div style="background: white; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; font-size: 14px; word-break: break-all;">'
            '{}'
            '</div>'
            '<div style="margin-top: 12px;">'
            '<button onclick="navigator.clipboard.writeText(\'{}\')" '
            'style="background: #417690; color: white; border: none; padding: 8px 16px; '
            'border-radius: 4px; cursor: pointer; font-size: 14px; margin-right: 10px;">'
            '📋 Скопировать ссылку'
            '</button>'
            '<span style="color: #666; font-size: 12px;">'
            'Вставьте эту ссылку в любой генератор QR-кодов'
            '</span>'
            '</div>'
            '</div>',
            full_url, full_url
        )
        except NoReverseMatch:
            return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 2px solid #79aec8;">'
            '<div style="margin-bottom: 10px;">'
            '<strong style="font-size: 16px; color: #417690;">📱 Ссылка для QR-кода сформируется после сохранения</strong>'
            '</div>'
            '</div>'
            
        )
        
        
        
    qr_redirect_link_display.short_description = 'Ссылка для генерации QR-кода'
    
    def qr_code_instructions(self, obj):
        """Инструкция по генерации QR-кода"""
        return format_html(
            '<div style="background: #e9f7ef; padding: 15px; border-radius: 8px; border-left: 4px solid #2b6e3c;">'
            '<strong style="color: #2b6e3c;">📝 Инструкция:</strong><br>'
            '1. Скопируйте ссылку выше<br>'
            '2. Перейдите на любой генератор QR-кодов (например, '
            '<a href="https://www.qr-code-generator.com/" target="_blank">qr-code-generator.com</a>, '
            '<a href="https://www.qrcode-monkey.com/" target="_blank">qrcode-monkey.com</a>, '
            'или <a href="https://goqr.me/" target="_blank">goqr.me</a>)<br>'
            '3. Вставьте скопированную ссылку в поле для генерации<br>'
            '4. Настройте дизайн QR-кода (цвет, логотип) по желанию<br>'
            '5. Скачайте готовый QR-код в формате PNG или SVG<br>'
            '6. Загрузите скачанный файл в поле "QR-код" ниже<br>'
            '</div>'
        )
    qr_code_instructions.short_description = 'Инструкция по генерации'
    
    def qr_code_preview(self, obj):
        """Показывает превью загруженного QR-кода"""
        if obj.qr_code:
            return format_html(
                '<div style="background: #f5f5f5; padding: 10px; border-radius: 4px; text-align: center;">'
                '<img src="{}" width="150" height="150" style="border: 1px solid #ddd; padding: 5px; background: white;" />'
                '<div style="margin-top: 8px;">'
                '<strong>✓ QR-код загружен</strong><br>'
                '<span style="color: #666; font-size: 11px;">Файл: {}</span>'
                '</div>'
                '</div>',
                obj.qr_code.url,
                obj.qr_code.name.split('/')[-1]
            )
        # elif obj.qr_code_url:
        #     return format_html(
        #         '<div style="background: #f5f5f5; padding: 10px; border-radius: 4px; text-align: center;">'
        #         '<img src="{}" width="150" height="150" style="border: 1px solid #ddd; padding: 5px; background: white;" />'
        #         '<div style="margin-top: 8px;">'
        #         '<strong>✓ Внешний QR-код</strong><br>'
        #         '<span style="color: #666; font-size: 11px;">URL: {}</span>'
        #         '</div>'
        #         '</div>',
        #         obj.qr_code_url,
        #         obj.qr_code_url[:50] + '...' if len(obj.qr_code_url) > 50 else obj.qr_code_url
        #     )
        else:
            return format_html(
                '<div style="background: #fff3cd; padding: 10px; border-radius: 4px; text-align: center; border: 1px solid #ffc107;">'
                '<span style="font-size: 32px;">⚠️</span><br>'
                '<strong>QR-код не загружен</strong><br>'
                '<span style="color: #856404; font-size: 12px;">Сгенерируйте QR-код по ссылке выше и загрузите его</span>'
                '</div>'
            )
    qr_code_preview.short_description = 'Превью QR-кода'
    
    def qr_code_status(self, obj):
        """Статус QR-кода для списка объектов"""
        if obj.qr_code:
            return format_html('<span style="color: #2b6e3c;">✓ Загружен</span>')
        return format_html('<span style="color: #dc3545;">✗ Не загружен</span>')
    qr_code_status.short_description = 'QR-код'
    
    def target_url_preview(self, obj):
        """Превью целевой ссылки"""
        if len(obj.target_url) > 50:
            return obj.target_url[:50] + '...'
        return obj.target_url
    target_url_preview.short_description = 'Целевая ссылка'
    
    def save_model(self, request, obj, form, change):
        """При сохранении очищаем одно из полей QR, если используется другое"""
        super().save_model(request, obj, form, change)
    
    actions = ['reset_statistics', 'show_qr_links']
    
    def reset_statistics(self, request, queryset):
        """Сброс статистики для выбранных ссылок"""
        for link in queryset:
            link.total_clicks = 0
            link.unique_clicks = 0
            link.save()
            ClickLog.objects.filter(link=link).delete()
        
        self.message_user(
            request, 
            f"Статистика сброшена для {queryset.count()} ссылок"
        )
    reset_statistics.short_description = "Сбросить статистику"
    
    def show_qr_links(self, request, queryset):
        """Показать ссылки для QR-кодов выбранных объектов"""
        links_info = []
        for link in queryset:
            full_url = f"{settings.BASE_URL}{link.get_absolute_url()}"
            links_info.append(f"{link.name}: {full_url}")
        
        self.message_user(
            request,
            "\n".join(links_info),
            level='INFO'
        )
    show_qr_links.short_description = "Показать ссылки для QR-кодов"


@admin.register(ClickLog)
class ClickLogAdmin(admin.ModelAdmin):
    list_display = ('link', 'clicked_at', 'ip_address', 'user_agent_preview')
    list_filter = ('link', 'clicked_at')
    search_fields = ('link__name', 'ip_address', 'session_key')
    readonly_fields = ('link', 'clicked_at', 'ip_address', 'user_agent', 'referer', 'session_key')
    
    def user_agent_preview(self, obj):
        if len(obj.user_agent) > 50:
            return obj.user_agent[:50] + '...'
        return obj.user_agent
    user_agent_preview.short_description = 'User-Agent'
    
    def has_add_permission(self, request):
        return False