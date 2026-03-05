from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView


# views.py для простого API
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from apps.constructs.models import Product, ProductImage
import json


class IndexViews(TemplateView):
    template_name = 'constructs/index.html'


def catalog_view(request):
    """Отображение каталога с пагинацией по 8 товаров"""
    products = Product.objects.filter(is_active=True).prefetch_related('images')
    paginator = Paginator(products, 8)  # 8 товаров на страницу
    
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list
    }
    return render(request, 'constructs/catalog.html', context)

def product_detail_view(request, product_id):
    """Детальная информация о товаре (для модального окна)"""
    print(product_id)
    print(Product.objects.get(pk=product_id))
    product = get_object_or_404(
        Product,
        id=product_id, 
        is_active=True
    )
    
    # Формируем данные для JSON ответа
    data = {
        'id': product.id,
        'title': product.title,
        'article': product.article,
        'area': float(product.area) if product.area else None,
        'rooms_count': product.rooms_count,
        'bathrooms_count': product.bathrooms_count,
        'floors_count': float(product.floors_count) if product.floors_count else None,
        'description': product.description,
        'images': [
            {
                'url': img.image.url,
                'alt': img.alt or f"{product.title} - фото {idx+1}"
            } for idx, img in enumerate(product.images.all().order_by('order'))
        ]
    }
    
    return JsonResponse(data)

@csrf_exempt
def products_list(request):
    """Получение списка проектов с пагинацией"""
    page = int(request.GET.get('page', 1))
    page_size = 4
    
    products = Product.objects.filter(is_active=True).prefetch_related('images')
    paginator = Paginator(products, page_size)
    
    current_page = paginator.get_page(page)
    
    data = {
        'results': [],
        'next': current_page.has_next(),
        'previous': current_page.has_previous(),
        'count': paginator.count
    }
    
    for product in current_page:
        main_image = product.images.filter(is_main=True).first()
        if not main_image:
            main_image = product.images.first()
        
        data['results'].append({
            'id': product.id,
            'title': product.title,
            'area': float(product.area) if product.area else None,
            'main_image': {
                'url': main_image.image.url if main_image else None,
                'alt': main_image.alt if main_image else None
            } if main_image else None
        })
    
    return JsonResponse(data)

@csrf_exempt
def product_detail(request, product_id):
    """Получение детальной информации о проекте"""
    try:
        product = Product.objects.prefetch_related('images').get(id=product_id, is_active=True)
        
        # Характеристики
        characteristics = []
        if product.area:
            characteristics.append({'icon': '📐', 'label': 'Площадь', 'value': f'{product.area} м²'})
        if product.floors_count:
            floors_text = {1: 'Одноэтажный', 1.5: 'Полутораэтажный', 2: 'Двухэтажный'}
            value = floors_text.get(float(product.floors_count), f'{product.floors_count} этажа')
            characteristics.append({'icon': '🏗️', 'label': 'Этажность', 'value': value})
        if product.rooms_count:
            characteristics.append({'icon': '🛋️', 'label': 'Комнат', 'value': product.rooms_count})
        if product.bathrooms_count:
            characteristics.append({'icon': '🚿', 'label': 'Санузлов', 'value': product.bathrooms_count})
        
        # Изображения
        images = []
        for img in product.images.all().order_by('order'):
            images.append({
                'id': img.id,
                'url': img.image.url,
                'alt': img.alt or f"{product.title} - фото"
            })
        
        data = {
            'id': product.id,
            'title': product.title,
            'article': product.article,
            'description': product.description,
            'area': float(product.area) if product.area else None,
            'floors_count': float(product.floors_count) if product.floors_count else None,
            'rooms_count': product.rooms_count,
            'bathrooms_count': product.bathrooms_count,
            'characteristics': characteristics,
            'images': images
        }
        
        return JsonResponse(data)
        
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)