from django.urls import path
from .views import  ProductListView, ProductDetailView, yandex_feed

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('getfeed/', yandex_feed, name='feed'),
    path('<slug:product_slug>/', ProductDetailView.as_view(), name='detail'),
    
]