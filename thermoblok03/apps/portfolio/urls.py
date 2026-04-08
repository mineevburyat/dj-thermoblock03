from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'portfolio'


router = DefaultRouter()
router.register(r'districts', views.DistrictViewSet)
router.register(r'houses', views.HouseViewSet)
router.register(r'reviews', views.ReviewViewSet)


urlpatterns = [
    path('', views.portfolio_view, name='section'),
#     path('', views.index, name='index'),
    # path('', views.IndexView.as_view(), name='index'),
    path('map/districts/', views.DistrictViewSet.as_view({'get': 'list'}), 
         name='map-districts'),
    path('map/houses/', views.HouseViewSet.as_view({'get': 'list'}), 
         name='map-houses'),
    path('districts/<int:pk>/', views.district_detail, name='district_detail'),
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('reviews/<int:pk>/', views.review_detail, name='review_detail'),
    path('houses/', views.houses_list, name='houses_list'),
    path('houses/<int:pk>/', views.house_detail, name='house_detail'),
]