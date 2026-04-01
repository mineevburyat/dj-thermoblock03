# urls.py (приложения)
from django.urls import path
from .views import RedirectView

app_name = 'qr_tracker'  # пространство имен

urlpatterns = [
    path('<slug:slug>/', RedirectView.as_view(), name='redirect'),
]