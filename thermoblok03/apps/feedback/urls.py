from django.urls import path
from apps.feedback import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_ajax, name='save'),
    path('ajax/', views.feedback_ajax, name='ajax'),
    path('construction-modal/', views.construction_modal, name='construction_modal'),
    path('submit-request/', views.submit_construction_request, name='submit_construction_request'),
]