from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import  HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings

class IndexView(TemplateView):
    """Главная страница"""
    template_name = 'old/katalog.html'

class Tb300(TemplateView):
    """Главная страница"""
    template_name = 'old/instruction300.html'

class Tb400(TemplateView):
    """Главная страница"""
    template_name = 'old/instruction400.html'