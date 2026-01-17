from django.urls import path
from .views import  ListInstructionsView, Instructions300, Instructions400, DetailView, detail_instruction

app_name = 'instruction'

urlpatterns = [
    path('', ListInstructionsView.as_view(), name='list'),
    path('new/<int:pk>/', detail_instruction, name='detail'),
    path('tb300/', Instructions300.as_view(), name='tb300'),
    path('tb400/', Instructions400.as_view(), name='tb400'),
    
]