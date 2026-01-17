from django.contrib import admin

from .models import Feedback

# admin.site.register(Feedback)

@admin.register(Feedback)
class FeeadbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'connect_time')
