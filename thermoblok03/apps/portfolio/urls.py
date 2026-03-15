from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'portfolio'


router = DefaultRouter()
router.register(r'districts', views.DistrictViewSet)
router.register(r'houses', views.HouseViewSet)
router.register(r'reviews', views.ReviewViewSet)


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('map/districts/', views.DistrictViewSet.as_view({'get': 'list'}), 
         name='map-districts'),
    path('map/houses/', views.HouseViewSet.as_view({'get': 'list'}), 
         name='map-houses'),
]