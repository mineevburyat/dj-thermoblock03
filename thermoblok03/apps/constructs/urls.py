from django.urls import path
from .views import IndexViews

app_name = 'projects'

urlpatterns = [
    path('', IndexViews.as_view(), name='index'),
    
]