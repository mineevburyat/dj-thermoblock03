from django import template
from django.urls import reverse
from urllib.parse import urlparse, urlunparse

register = template.Library()

@register.simple_tag(takes_context=True)
def canonical_url(context, obj=None):
    request = context.get('request')
    if not request:
        return ''
    
    if obj and hasattr(obj, 'get_absolute_url'):
        # Для объектов с get_absolute_url
        path = obj.get_absolute_url()
    else:
        # Берем текущий путь без параметров
        parsed = urlparse(request.get_full_path())
        path = urlunparse(parsed._replace(query='', fragment=''))
    
    return request.build_absolute_uri(path)