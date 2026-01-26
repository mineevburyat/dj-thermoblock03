from django.urls import path
from .views import IndexView, Tb300, Tb400


app_name = 'old'


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('tb300/', Tb300.as_view(), name='tb300'),
    path('tb400/', Tb400.as_view(), name='tb400'),
]

