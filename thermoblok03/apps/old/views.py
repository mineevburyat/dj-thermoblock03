from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import  HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings


class HomeNewView(TemplateView):
    """Главная новая страница на утверждение"""
    template_name = 'old/index_new.html'

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

def custom_400(request, exception):
    # Передайте контекст, если нужно, но для 400-й это может быть опасно
    return render(request, 'my_errors/400.html', status=400)

def custom_500(request):
    # Для 500 НЕ передавайте сложные данные в контекст
    return render(request, 'my_errors/500.html', status=500)