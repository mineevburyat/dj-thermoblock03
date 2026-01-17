from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.utils.timezone import now
# Create your views here.
from .models import Products


class ProductListView(ListView):
    model = Products
    template_name = 'products/list.html'
    context_object_name = 'products'
    
class ProductDetailView(DetailView):
    model = Products
    template_name = 'products/detail.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = "product"
    ordering = ("pk",)
    
def yandex_feed(request):
    products = Products.objects.all()
    context = {
        'products': products,
        'now': now().strftime("%Y-%m-%dT%H:%M"),
        'url': 'https://thermoblock03.ru'
    }
    return render(request,
                  template_name='products/yandex_feed.xml',
                  context=context,
                  content_type='application/xml')