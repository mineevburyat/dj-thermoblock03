from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class AllProjects(TemplateView):
    template_name = 'projects/main.html'