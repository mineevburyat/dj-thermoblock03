from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from django.views.generic import RedirectView

# from products.models import Products
from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type="text/plain")),
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path('', include('apps.old.urls', namespace='home')),
    # path('catalog/', include('apps.old.urls', namespace='catalog')),
    path('about/', include('apps.about.urls', namespace='about')),
    path('feedback/', include('apps.feedback.urls', namespace='feedback')),
    # path('instructions/', include('apps.instructions.urls', namespace='instructions')),
    path('constructs/', include('apps.constructs.urls', namespace='constructs')),
    path('products/', include('apps.products.urls', namespace='products')),
    # path('captcha/', include('captcha.urls')),
    # path('faq/', include('apps.faq.urls', namespace='faq')),
    path('portfolio/', include('apps.portfolio.urls', namespace='portfolio')),
    path('qr/', include('apps.qr_tracker.urls', namespace='qr_tracker')),
    
    path('instructions/tb300/', RedirectView.as_view(url='/tb300/'), name='old-tb300'),
    path('instructions/tb400/', RedirectView.as_view(url='/tb400/'), name='old-tb400'),
    path('catalog/instrukcziya-po-proizvodstvu-rabot-iz-teploizolyaczionnyix-blokov.html', RedirectView.as_view(url='/tb400/'), name='old-incruct'),
    path('instructions/', RedirectView.as_view(url='/tb400/'), name='old-all-incruct'),
    path('instructions/tb400/index.html', RedirectView.as_view(url='/tb400/'), name='old-tb400-incruct'),
    path('index.html', RedirectView.as_view(url='/'), name='old-index'),
    path('catalog/', RedirectView.as_view(url='constructs/'), name='projects'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
