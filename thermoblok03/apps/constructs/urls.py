from django.urls import path
from .views import IndexViews, catalog_view, product_detail_view

app_name = 'projects'

urlpatterns = [
    path('', catalog_view, name='index'),
    # path('api/', products_list, name='api_list'),
    path('api/product/<int:product_id>/', product_detail_view, name='api_detail'),
]