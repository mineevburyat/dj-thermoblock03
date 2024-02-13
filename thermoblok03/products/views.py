from django.shortcuts import render
from django.views.generic import ListView, DetailView
# Create your views here.
from .models import Products


class ProductListView(ListView):
    model = Products
    template_name = 'products/list.html'
    
class ProductDetailView(DetailView):
    model = Products
    template_name = 'products/detail.html'