from django.urls import path
from .views import  ProductListView, ProductDetailView, IndexView, yandex_feed

app_name = 'products'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('getfeed/', yandex_feed, name='feed'),
    path('<slug:product_slug>/', ProductDetailView.as_view(), name='detail'),
    
]