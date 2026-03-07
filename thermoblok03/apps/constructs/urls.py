from django.urls import path
from .views import IndexViews, catalog_view, product_detail_view, product_edit, toggle_active, set_main_image, delete_image, reorder_images

app_name = 'constructs'

urlpatterns = [
    path('', catalog_view, name='index'),
    # path('api/', products_list, name='api_list'),
    path('api/product/<int:product_id>/', product_detail_view, name='api_detail'),
    path('detail/<int:product_id>/', product_edit, name='product-edit'),
    path('detail/<int:product_id>/toggle-active/', toggle_active, name='project-toggle-active'),
    path('detail/<int:product_id>/set-main-image/<int:image_id>/', set_main_image, name='product-set-main-image'),
    path('detail/<int:product_id>/delete-image/<int:image_id>/', delete_image, name='product-delete-image'),
    path('detail/<int:product_id>/reorder-images/', reorder_images, name='product-reorder-images'),]