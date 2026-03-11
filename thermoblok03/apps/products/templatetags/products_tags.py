from django import template
from django.utils.safestring import mark_safe
from ..models import BlockSeries

register = template.Library()

@register.inclusion_tag('products/_products_section.html', takes_context=True)
def show_series_cards(context, limit=None, series_type=None, show_title=True):
    """
    Шаблонный тег для отображения карточек серий блоков
    
    Параметры:
    - limit: ограничение количества выводимых серий
    - series_type: фильтр по типу серии ('monolithic' или 'block')
    - show_title: показывать ли заголовок "Серии термоблоков"
    
    Пример использования:
    {% load catalog_tags %}
    {% show_series_cards limit=6 %}
    {% show_series_cards series_type='monolithic' %}
    {% show_series_cards limit=4 show_title=False %}
    """
    
    queryset = BlockSeries.objects.filter(is_active=True).prefetch_related(
        'blocks', 'characteristic_groups', 'linked_media'
    ).select_related('main_image')
    
    if series_type:
        queryset = queryset.filter(series_type=series_type)
    
    if limit:
        queryset = queryset[:limit]
    
    # Добавляем дополнительные данные для каждой серии
    series_list = []
    for series in queryset:
        groups = series.characteristic_groups.all()
        series_data = {
            'series': series,
            'blocks_count': series.blocks.count(),
            'thickness_range': get_thickness_range(groups),
            'first_thickness': groups.first().wall_thickness if groups else None,
            'last_thickness': groups.last().wall_thickness if groups.count() > 1 else None,
            'has_multiple_thickness': groups.count() > 1,
        }
        series_list.append(series_data)
    
    return {
        'series_list': series_list,
        'show_title': show_title,
        'request': context.get('request'),
    }

@register.simple_tag
def get_series_count(series_type=None):
    """Возвращает количество активных серий"""
    queryset = BlockSeries.objects.filter(is_active=True)
    if series_type:
        queryset = queryset.filter(series_type=series_type)
    return queryset.count()

@register.filter
def thickness_display(series):
    """Форматирует отображение толщин для серии"""
    groups = series.characteristic_groups.all()
    if not groups:
        return ''
    
    thicknesses = [str(g.wall_thickness) for g in groups]
    if len(thicknesses) == 1:
        return f'{thicknesses[0]} мм'
    else:
        return f'{thicknesses[0]}-{thicknesses[-1]} мм'

# Вспомогательная функция
def get_thickness_range(groups):
    """Возвращает диапазон толщин для отображения"""
    if not groups:
        return None
    thicknesses = [g.wall_thickness for g in groups]
    if len(thicknesses) == 1:
        return thicknesses[0]
    return f'{min(thicknesses)}-{max(thicknesses)}'