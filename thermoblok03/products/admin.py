from .models import Products, Characteristics, MediaProduct
from django.contrib import admin

# Register your models here.
# admin.site.register(Products)
admin.site.register(Characteristics)
admin.site.register(MediaProduct)

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ("title", "subtitle")
            }
        ),
        (
            "Габариты и вес",
            {
                "fileds": (("length", "width", "height"),
                            ("block_weight", "blocks_in_paddon"))
            }
        ),
        (
            "Характеристики",
            {
                "fileds": ("soundproofing",
                           ("concrete", "block_consumption"))
            }
        ),
         ("Изображение",
          {
              "fileds": ("images",)
          })

    ]

[
        (
            None,
            {
                "fields": ["url", "title", "content", "sites"],
            },
        ),
        (
            "Advanced options",
            {
                "classes": ["collapse"],
                "fields": ["registration_required", "template_name"],
            },
        ),
    ]
