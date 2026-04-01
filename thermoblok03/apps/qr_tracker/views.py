# views.py
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views import View
from .models import TrackedLink

@method_decorator(never_cache, name='dispatch')
class RedirectView(View):
    """Редирект с записью статистики"""
    
    def get(self, request, slug):
        link = get_object_or_404(TrackedLink, slug=slug, is_active=True)
        link.increment_click(request)
        return redirect(link.target_url)