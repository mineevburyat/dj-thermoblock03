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
        context['building_types'] = [
            ('house', 'Жилой дом'),
            ('extension', 'Пристройка/Пристрой'),
            ('garage', 'Гараж'),
            ('banya', 'Баня/Сауна'),
            ('office', 'Офисное здание'),
            ('warehouse', 'Производственное помещение/Склад'),
            ('greenhouse', 'Теплица/Оранжерея'),
            ('other', 'Другое'),
        ]
        context['floor_options'] = [
            ('1', 'Одноэтажный'),
            ('1.5', 'Полутораэтажный'),
            ('2', 'Двухэтажный'),
            ('2+', 'Более двух этажей'),
            ('mansard', 'С мансардой'),
            ('undecided', 'Еще думаю/Нужна консультация'),
        ]
        context['features'] = [
            ('basement', 'Цокольный этаж/подвал'),
            ('terrace', 'Терраса/веранда'),
            ('balcony', 'Балкон'),
            ('garage_included', 'Встроенный гараж'),
            ('pool', 'Бассейн'),
            ('sauna', 'Сауна/хамам'),
        ]
        
        context['project_options'] = [
            ('has_project', 'Имеется готовый проект'),
            ('has_sketch', 'Есть только эскиз/наброски'),
            ('need_consultation', 'Нужна консультация для разработки проекта'),
        ]
    
        return context
