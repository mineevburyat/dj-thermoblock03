from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.defaults import page_not_found, server_error

from django.template import engines

class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'home/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ThermoBlock | Главная страница'
        return context
