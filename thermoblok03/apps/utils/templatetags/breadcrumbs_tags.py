from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()

class Breadcrumbs:
    """Класс для управления хлебными крошками"""
    
    def __init__(self, request):
        self.request = request
        self.crumbs = []
        self._initialized = False
        
        # Пытаемся восстановить из сессии, если нужно
        self._load_from_session()
    
    def _load_from_session(self):
        """Загружаем сохранённые крошки из сессии"""
        if hasattr(self.request, 'session'):
            session_key = f'breadcrumbs_{self.request.path}'
            if session_key in self.request.session:
                self.crumbs = self.request.session[session_key]
                self._initialized = True
    
    def _save_to_session(self):
        """Сохраняем крошки в сессию"""
        if hasattr(self.request, 'session') and self.crumbs:
            # Очищаем старые записи для этого пути
            session_key = f'breadcrumbs_{self.request.path}'
            self.request.session[session_key] = self.crumbs
    
    def add(self, title, url=None, persistent=True):
        """
        Добавляет крошку
        
        Args:
            title: Название или функция для получения названия
            url: URL или имя URL-паттерна
            persistent: Сохранять ли в сессии
        """
        # Если title - функция, вызываем её
        if callable(title):
            title = title()
            
        # Если url - имя URL-паттерна, пробуем его разрешить
        if url and not url.startswith('/'):
            try:
                url = reverse(url)
            except NoReverseMatch:
                # Если не удалось разрешить, оставляем как есть
                pass
        
        crumb = {
            'title': str(title),
            'url': url,
            'is_active': url == self.request.path if url else True
        }
        
        self.crumbs.append(crumb)
        
        if persistent:
            self._save_to_session()
        
        return crumb
    
    def reset(self):
        """Очищает все крошки"""
        self.crumbs = []
        if hasattr(self.request, 'session'):
            # Очищаем все ключи breadcrumbs в сессии
            keys_to_delete = [k for k in self.request.session.keys() 
                            if k.startswith('breadcrumbs_')]
            for key in keys_to_delete:
                del self.request.session[key]

@register.simple_tag(takes_context=True)
def get_breadcrumbs(context):
    """
    Получает объект breadcrumbs для текущего запроса
    Использование: {% get_breadcrumbs as breadcrumbs %}
    """
    request = context.get('request')
    if not request:
        return None
    
    if not hasattr(request, 'breadcrumbs'):
        request.breadcrumbs = Breadcrumbs(request)
    
    return request.breadcrumbs

@register.inclusion_tag('core/breadcrumbs.html', takes_context=True)
def render_breadcrumbs(context, **kwargs):
    """
    Рендерит хлебные крошки
    
    Аргументы:
        separator: разделитель (по умолчанию: '/')
        home_title: название главной страницы (по умолчанию: 'Главная')
        home_url: URL главной страницы (по умолчанию: '/')
        template: шаблон для рендеринга
    """
    request = context.get('request')
    if not request or not hasattr(request, 'breadcrumbs'):
        return {'breadcrumbs': []}
    
    breadcrumbs = request.breadcrumbs.crumbs.copy()
    print(breadcrumbs)
    # Добавляем главную страницу, если её нет
    home_title = kwargs.get('home_title', _('Главная'))
    home_url = kwargs.get('home_url', '/')
    
    if not breadcrumbs or breadcrumbs[0].get('url') != home_url:
        breadcrumbs.insert(0, {
            'title': home_title,
            'url': home_url,
            'is_active': False
        })
    
    # Отмечаем последний элемент как активный
    if breadcrumbs:
        breadcrumbs[-1]['is_active'] = True
        if breadcrumbs[-1].get('url'):
            # Убираем URL у последнего элемента
            breadcrumbs[-1]['url'] = None
    
    return {
        'breadcrumbs': breadcrumbs,
        'separator': kwargs.get('separator', '/'),
    }

@register.simple_tag(takes_context=True)
def add_breadcrumb(context, title, url=None, persistent=True):
    """
    Добавляет крошку в текущий запрос
    
    Использование: {% add_breadcrumb "Каталог" "catalog:list" %}
    """
    request = context.get('request')
    if request:
        if not hasattr(request, 'breadcrumbs'):
            request.breadcrumbs = Breadcrumbs(request)
        return request.breadcrumbs.add(title, url, persistent)
    return ''

@register.simple_tag(takes_context=True)
def auto_breadcrumbs(context):
    """
    Автоматически генерирует крошки на основе URL и моделей
    
    Использование: {% auto_breadcrumbs %}
    """
    request = context.get('request')
    if not request or not hasattr(request, 'breadcrumbs'):
        return ''
    
    # Если крошки уже есть, не генерируем заново
    if request.breadcrumbs.crumbs:
        return ''
    
    # Автоматическая генерация на основе URL
    path_parts = request.path.strip('/').split('/')
    current_url = ''
    
    for i, part in enumerate(path_parts):
        current_url += '/' + part
        
        # Пытаемся получить название из URL или модели
        title = part.replace('-', ' ').replace('_', ' ').title()
        
        # Проверяем, не является ли это ID модели
        if i < len(path_parts) - 1 and path_parts[i+1].isdigit():
            # Это может быть список моделей
            model_name = part.rstrip('s')  # убираем 's' на конце
            title = model_name.title() + 's'
        
        # Проверяем, не последний ли это элемент
        is_last = (i == len(path_parts) - 1)
        
        request.breadcrumbs.add(
            title=title,
            url=None if is_last else current_url,
            persistent=False
        )
    
    return ''

@register.simple_tag
def breadcrumb_schema():
    return "http://schema.org/BreadcrumbList"


@register.inclusion_tag('core/breadcrumb.html')
def breadcrumb_home(url='/', title=''):
    return {
        'url': url,
        'title': title
    }
