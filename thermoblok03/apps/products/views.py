from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.timezone import now
from .models import Products


class IndexView(TemplateView):
    template_name = 'products/index5.html'

class ProductAllView(TemplateView):
    model = Products
    template_name = 'products/product.html'
    
class ProductDetailView(DetailView):
    model = Products
    template_name = 'products/detail.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = "product"
    ordering = ("pk",)
    
# def yandex_feed(request):
#     products = Products.objects.all()
#     context = {
#         'products': products,
#         'now': now().strftime("%Y-%m-%dT%H:%M"),
#         'url': 'https://thermoblock03.ru'
#     }
#     return render(request,
#                   template_name='products/yandex_feed.xml',
#                   context=context,
#                   content_type='application/xml')


