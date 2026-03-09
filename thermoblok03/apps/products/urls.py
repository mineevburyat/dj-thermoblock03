from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.SeriesListView.as_view(), name='series_list'),
    path('series/<slug:slug>/', views.SeriesDetailView.as_view(), name='series_detail'),
]