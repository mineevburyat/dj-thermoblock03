# breadcrumbs/mixins.py
import importlib
from django.urls import resolve, reverse
from django.views.generic.detail import SingleObjectMixin

class BreadcrumbMixin:
    breadcrumbs = []  # можно переопределить в конкретном представлении
    
    def get_breadcrumbs(self):
        # Базовая логика: всегда добавляем "Главная"
        breadcrumbs = [('Главная', reverse('home'))]
        
        # Если breadcrumbs определены в классе - используем их
        if hasattr(self, 'breadcrumbs') and self.breadcrumbs:
            breadcrumbs.extend(self.breadcrumbs)
            return breadcrumbs
            
        # Автоматическая генерация для детальных представлений
        if isinstance(self, SingleObjectMixin) and hasattr(self, 'get_object'):
            obj = self.get_object()
            app_label = obj._meta.app_label
            model_name = obj._meta.model_name
            
            # Пытаемся найти список объектов
            list_url = reverse(f'{app_label}:{model_name}_list')
            breadcrumbs.append((obj._meta.verbose_name_plural.title(), list_url))
            breadcrumbs.append((str(obj), None))  # текущая страница без ссылки
            
        return breadcrumbs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context