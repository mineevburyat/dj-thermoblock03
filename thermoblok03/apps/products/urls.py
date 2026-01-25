from django.urls import path
from .views import  ProductAllView, ProductDetailView, IndexView

app_name = 'products'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('all/', IndexView.as_view(), name='all'),
    # path('getfeed/', yandex_feed, name='feed'),
    path('<slug:product_slug>/', ProductDetailView.as_view(), name='detail'),
    
]