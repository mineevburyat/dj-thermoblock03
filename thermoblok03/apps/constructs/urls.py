from django.urls import path
from .views_ed import catalog_view, toggle_active, set_main_image, delete_image, reorder_images, project_list, product_detail_1
from .views import product_list, product_detail, product_edit

app_name = 'constructs'

urlpatterns = [
    path('', product_list, name='index'),
    path('<slug:slug>/', product_detail, name='project_detail'),
    # path('api/', products_list, name='api_list'),
    # path('api/product/<int:product_id>/', product_detail_view, name='api_detail'),
    path('test/', catalog_view, name='test_index'),
    path('edit/<int:product_id>/', product_edit, name='product-edit'),
    path('edit/<int:product_id>/toggle-active/', toggle_active, name='project-toggle-active'),
    path('edit/<int:product_id>/set-main-image/<int:image_id>/', set_main_image, name='product-set-main-image'),
    path('edit/<int:product_id>/delete-image/<int:image_id>/', delete_image, name='product-delete-image'),
    path('edit/<int:product_id>/reorder-images/', reorder_images, name='product-reorder-images'),]