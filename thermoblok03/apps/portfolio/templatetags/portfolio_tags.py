from django import template
from django.db.models import Count, Avg, Q, Prefetch
from django.core.paginator import Paginator
from ..models import District, House, Review, HouseMedia

# register = template.Library()

# @register.inclusion_tag('portfolio/latest_houses.html', takes_context=True)
# def latest_houses_section(context, count=6, columns=3):
#     """
#     Шаблонный тег для секции с последними домами
#     Использование: {% latest_houses_section count=6 columns=3 %}
#     """
#     houses = House.objects.filter(
#         status='built'
#     ).select_related('district').prefetch_related(
#         Prefetch(
#             'media',
#             queryset=HouseMedia.objects.filter(is_primary=True),
#             to_attr='primary_media'
#         )
#     ).annotate(
#         reviews_count=Count('reviews', filter=Q(reviews__is_published=True)),
#         average_rating=Avg('reviews__rating', filter=Q(reviews__is_published=True))
#     ).order_by('-created_at')[:count]
    
#     # Добавляем primary_image для каждого дома
#     for house in houses:
#         house.primary_image = house.primary_media[0] if house.primary_media else None
    
#     return {
#         'houses': houses,
#         'columns': columns,
#         'request': context.get('request'),
#     }


# @register.inclusion_tag('portfolio/latest_reviews.html', takes_context=True)
# def latest_reviews_section(context, count=3, show_house=True):
#     """
#     Шаблонный тег для секции с последними отзывами
#     Использование: {% latest_reviews_section count=3 show_house=True %}
#     """
#     reviews = Review.objects.filter(
#         is_published=True
#     ).select_related(
#         'house',
#         'house__district'
#     ).prefetch_related(
#         'photos'
#     ).order_by('-created_at')[:count]
    
#     return {
#         'reviews': reviews,
#         'show_house': show_house,
#         'request': context.get('request'),
#     }


# @register.inclusion_tag('portfolio/districts_map.html', takes_context=True)
# def districts_map_section(context, height='500px', show_houses=True):
#     """
#     Шаблонный тег для секции с картой районов
#     Использование: {% districts_map_section height='400px' show_houses=True %}
#     """
#     districts = District.objects.annotate(
#         total_houses=Count('houses', filter=Q(houses__status='built'))
#     ).order_by('name').values('id', 'name', 'center_latitude', 'center_longitude', 'total_houses')
    
#     # Получаем последние дома для отображения в балунах
#     latest_houses = {}
#     if show_houses:
#         for district in districts:
#             latest_houses[district.id] = district.houses.filter(
#                 status='built'
#             ).select_related('district')[:3]
    
#     return {
#         'districts': districts,
#         'latest_houses': latest_houses,
#         'map_height': height,
#         'show_houses': show_houses,
#         'yandex_api_key': context.get('yandex_api_key', ''),
#         'request': context.get('request'),
#     }


# @register.inclusion_tag('portfolio/paginated_houses.html', takes_context=True)
# def paginated_houses_section(context, per_page=9, template='grid'):
#     """
#     Шаблонный тег для секции с пагинацией домов
#     Использование: {% paginated_houses_section per_page=9 template='grid' %}
#     """
#     page = context.get('request').GET.get('houses_page', 1)
    
#     houses_list = House.objects.filter(
#         status='built'
#     ).select_related('district').prefetch_related(
#         Prefetch(
#             'media',
#             queryset=HouseMedia.objects.filter(is_primary=True),
#             to_attr='primary_media'
#         )
#     ).annotate(
#         reviews_count=Count('reviews', filter=Q(reviews__is_published=True)),
#         average_rating=Avg('reviews__rating', filter=Q(reviews__is_published=True))
#     ).order_by('-created_at')
    
#     paginator = Paginator(houses_list, per_page)
#     houses = paginator.get_page(page)
    
#     # Добавляем primary_image для каждого дома
#     for house in houses:
#         house.primary_image = house.primary_media[0] if house.primary_media else None
    
#     return {
#         'houses': houses,
#         'template_type': template,
#         'request': context.get('request'),
#     }


# @register.inclusion_tag('portfolio/paginated_reviews.html', takes_context=True)
# def paginated_reviews_section(context, per_page=5):
#     """
#     Шаблонный тег для секции с пагинацией отзывов
#     Использование: {% paginated_reviews_section per_page=5 %}
#     """
#     page = context.get('request').GET.get('reviews_page', 1)
    
#     reviews_list = Review.objects.filter(
#         is_published=True
#     ).select_related(
#         'house',
#         'house__district'
#     ).order_by('-created_at')
    
#     paginator = Paginator(reviews_list, per_page)
#     reviews = paginator.get_page(page)
    
#     return {
#         'reviews': reviews,
#         'request': context.get('request'),
#     }

# @register.filter
# def sum_houses(districts):
#     """Суммирует количество домов во всех районах"""
#     return sum(d.houses_count for d in districts)

# @register.filter
# def get_item(dictionary, key):
#     """Получает элемент из словаря по ключу"""
#     return dictionary.get(key)


register = template.Library()

@register.inclusion_tag('portfolio/_portfolio_section.html', takes_context=True)
def show_portfolio_section(context, limit=4, title='Наши проекты', show_controls=True):
    """
    Тег для вывода секции портфолио на любой странице
    
    Использование:
        {% load portfolio_tags %}
        {% show_portfolio_section limit=6 title="Построенные дома" show_controls=True %}
    
    Параметры:
        limit - количество отображаемых домов (по умолчанию 10)
        title - заголовок секции
        show_controls - показывать кнопки скролла (True/False)
    """
    # Получаем дома, можно фильтровать по статусу
    houses = House.objects.filter(Q(status='built')).order_by('order')[:limit]
    
    total_count = houses.count()
    
    return {
        'houses': houses,
        'total_count': total_count,
        'section_title': title,
        'show_controls': show_controls,
        'request': context.get('request'),
    }


@register.simple_tag
def get_portfolio_count(status=None):
    """Возвращает количество домов в портфолио"""
    if status:
        return House.objects.filter(status=status).count()
    return House.objects.count()