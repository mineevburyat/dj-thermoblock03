from django.urls import path
from .views import IndexView, PrivacyView, AgreementView, ContactView
app_name = 'about'


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('agreement/', AgreementView.as_view(), name='agreement'),
    path('contact/', ContactView.as_view(), name='contact'),
]

