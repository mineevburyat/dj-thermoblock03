from .models import Products, Characteristics, MediaProduct
from django.contrib import admin

# Register your models here.
# admin.site.register(Products)
admin.site.register(Characteristics)
admin.site.register(MediaProduct)

class CharacteristicsInline(admin.TabularInline):
    model = Characteristics
    extra = 0

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    inlines = (CharacteristicsInline, )
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
                "fields": (("length", "width", "height"),
                            ("block_weight", "blocks_in_paddon"))
            }
        ),
        (
            "Характеристики",
            {
                "fields": ("soundproofing",
                           ("concrete", "block_consumption"))
            }
        ),
         ("Изображение",
          {
              "fields": ("images",)
          })

    ]

