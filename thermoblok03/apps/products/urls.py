from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.CatalogView.as_view(), name='catalog'),
    # path('series/', views.SeriesListView.as_view(), name='series_list'),
    path('series/<slug:slug>/', views.SeriesDetailViewNew.as_view(), name='series_detail'),
    path('series/old/<slug:slug>/', views.SeriesDetailView.as_view(), name='series_detail_old'),
    # path('api/blocks/<int:series_id>/', views.get_blocks_json, name='get_blocks_json'),
    # path('api/calculate/', views.calculate_materials, name='calculate'),
]