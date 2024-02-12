from django.urls import path
from .views import feedback_save

app_name = 'feedback'

urlpatterns = [
    path('', feedback_save, name='save')
]