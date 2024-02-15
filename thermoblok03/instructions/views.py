from django.shortcuts import render
from django.views.generic.base import TemplateView
from .models import Instractions, Stage, Recomendation
from django.views.generic import ListView
from django.views.generic.detail import DetailView

class AllInstructions(TemplateView):
    template_name = 'instructions/list.html'

class Instructions300(TemplateView):
    template_name = 'instructions/tb300.html'

class Instructions400(TemplateView):
    template_name = 'instructions/tb400.html'

class ListInstructionsView(ListView):
    template_name = 'instructions/list.html'
    model = Instractions
    context_object_name = 'instructions'

class DetailInstructionView(DetailView):
    model = Instractions
    template_name = 'instructions/detail.html'
    context_object_name = 'instruction'
    
def detail_instruction(request, pk):
    qs = Instractions.objects.get(pk=pk)
    context = {
        'instruction': qs
    }
    return render(request, template_name='instructions/detail.html', context=context)