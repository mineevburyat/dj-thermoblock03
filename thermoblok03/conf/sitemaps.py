from django.contrib import sitemaps
from django.urls import reverse
from django.utils import timezone
from django.conf import settings 
from datetime import date


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 1
    changefreq = "weekly"
    protocol = 'https'
    

    def items(self):
        return ["home:index", "about:contact", "about:privacy"]

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return date(2026,1, 14)
        
    # def get_urls(self, **kwargs):
    #     # Формируем базовый URL
    #     base_url = f"https://"
    #     base_url += settings.ALLOWED_HOSTS[0]  # берем первый домен из настроек
        
    #     urls = []
    #     for item in self.items():
    #         path = self.location(item)
    #         urls.append({
    #             'location': f"{base_url}{path}",
    #             'changefreq': getattr(self, 'changefreq', 'daily'),
    #             'priority': str(getattr(self, 'priority', 0.5)),
    #             'lastmod': str(getattr(self,'lastmod', '27.01.2026'))
    #         })
    #     return urls