from django import template
from django.db.models import Count, Q
from ..models import Product, ProductType

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()


@register.inclusion_tag('constructs/_section.html', takes_context=True)
def show_projects_preview(context, limit=3, show_categories=True):
    """Универсальный тег для показа превью проектов"""
    request = context.get('request')
    
    projects = Product.objects.filter(is_active=True).order_by('id')[:limit]
    
    categories = None
    if show_categories:
        categories = ProductType.objects.annotate(
            products_count=Count('products', filter=Q(products__is_active=True))
        ).filter(products_count__gt=0)
    
    return {
        'projects': projects,
        'categories': categories,
        'favorites': request.session.get('favorites', []) if request else [],
        'request': request,
    }

@register.inclusion_tag('catalog/includes/popular_projects.html', takes_context=True)
def show_popular_projects(context, limit=4):
    """Отдельный тег для популярных проектов"""
    # Логика для популярных проектов
    pass