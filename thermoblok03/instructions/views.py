from django.shortcuts import render
from django.views.generic.base import TemplateView

class AllInstructions(TemplateView):
    template_name = 'instructions/list.html'


class Instructions300(TemplateView):
    template_name = 'instructions/tb300.html'

class Instructions400(TemplateView):
    template_name = 'instructions/tb400.html'