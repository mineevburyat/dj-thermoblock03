from django.urls import path
from .views import  AllInstructions, Instructions300, Instructions400

app_name = 'instruction'

urlpatterns = [
    path('', AllInstructions.as_view(), name='list'),
    path('tb300/', Instructions300.as_view(), name='tb300'),
    path('tb400/', Instructions400.as_view(), name='tb400'),
]