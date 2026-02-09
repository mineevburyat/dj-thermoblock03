from django.urls import path
from .views import HomeView, CatalogView, Tb300, Tb400


app_name = 'old'


urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('tb300/', Tb300.as_view(), name='tb300'),
    path('tb400/', Tb400.as_view(), name='tb400'),
]

