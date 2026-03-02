from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import  HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings



class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'old/index.html'

class CatalogView(TemplateView):
    """Главная страница"""
    template_name = 'old/katalog.html'

class Tb300(TemplateView):
    """Главная страница"""
    template_name = 'old/instruction300.html'

class Tb400(TemplateView):
    """Главная страница"""
    template_name = 'old/instruction400.html'

class Portfolio(TemplateView):
    """Главная страница"""
    template_name = 'old/portfolio.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["portfolioData"] = {
                1: {
                    'title': "Уютный дом в скандинавском стиле",
                    'description': "Полное описание проекта. Здесь можно рассказать об особенностях планировки, использованных материалах и сроках строительства. Дом построен для семьи с двумя детьми.",
                    'price': "5 500 000 ₽",
                    'area': "143 м²",
                    'images': [
                        "/media/portfolio/dom1-render.webp",
                        "/media/portfolio/dom1-profil.webp",
                        "/media/portfolio/dom1-plan1.webp",
                        "/media/portfolio/dom1-kitchen.webp",
                        "/media/portfolio/dom1-hol.webp",
                    ]
                },
                2: {
                    'title': "Современный дом с террасой",
                    'description': "Описание второго проекта. Просторный дом для загородного проживания. Большая остекленная терраса и второй свет в гостиной.",
                    'price': "7 200 000 ₽",
                    'area': "168 м²",
                    'images': [
                        "/media/portfolio/dom2-render.webp",
                        "/media/portfolio/dom2-profil.webp",
                    ]
                },
                3: {
                    'title': "Современный дом с террасой",
                    'description': "Описание третьего проекта. Просторный дом для загородного проживания. Большая остекленная терраса и второй свет в гостиной.",
                    'price': "7 200 000 ₽",
                    'area': "168 м²",
                    'images': [
                        "/media/portfolio/dom3-render.webp",
                        "/media/portfolio/dom3-profil.webp",
                    ]
                }
            }
        return context
    