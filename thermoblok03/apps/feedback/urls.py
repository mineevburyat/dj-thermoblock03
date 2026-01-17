from django.urls import path
from .views import feedback_save, feedback_ajax

app_name = 'feedback'

urlpatterns = [
    path('', feedback_ajax, name='save'),
    path('ajax/', feedback_ajax, name='ajax')
]