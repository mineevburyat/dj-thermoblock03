from django.urls import path
from .views import AllProjects

app_name = 'projects'

urlpatterns = [
    path('', AllProjects.as_view(), name='main'),
    
]