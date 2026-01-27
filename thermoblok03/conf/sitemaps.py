from django.contrib import sitemaps
from django.urls import reverse
from django.utils import timezone
from django.conf import settings 


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 1
    changefreq = "daily"
    protocol = 'https'
    

    def items(self):
        return ["home:index"]

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        print(timezone.now())
        return timezone.now()
        
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