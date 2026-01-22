from django.urls import path
from apps.feedback import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_ajax, name='save'),
    path('ajax/', views.feedback_ajax, name='ajax'),
    path('construction-modal/', views.construction_modal, name='construction_modal'),
    path('submit-request1/', views.submit_construction_request, name='submit_construction_request'),
    path('question/', views.QuestionViews.as_view(), name='question'),
    path('request/', views.submit_request, name='submit_request'),
]