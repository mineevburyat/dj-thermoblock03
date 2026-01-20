from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap

# from products.models import Products
from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type="text/plain")),
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path('', include('apps.home.urls', namespace='home')),
    path('about/', include('apps.about.urls', namespace='about')),
    path('feedback/', include('apps.feedback.urls', namespace='feedback')),
    path('instructions/', include('apps.instructions.urls', namespace='instructions')),
    path('constructs/', include('apps.house_projects.urls', namespace='constructs')),
    path('products/', include('apps.products.urls', namespace='products')),
    path('captcha/', include('captcha.urls')),
    path('faq/', include('apps.faq.urls', namespace='faq')),
    path('review/', include('apps.review.urls', namespace='review')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
