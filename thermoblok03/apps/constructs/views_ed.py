from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView

from django.views.decorators.http import require_POST
# views.py для простого API
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from apps.constructs.models import Product, ProductImage, ProductType, RoofType
import json
from django.db.models import Prefetch, Max
from django.contrib import messages
from django.db.models import Q


def project_list(request):
    projects = Product.objects.filter(is_active=True)
    
    # Фильтр по площади
    area_min = request.GET.get('area_min')
    area_max = request.GET.get('area_max')
    if area_min:
        projects = projects.filter(area__gte=area_min)
    if area_max:
        projects = projects.filter(area__lte=area_max)
    
    # Фильтр по комнатам
    rooms = request.GET.getlist('rooms')
    if rooms:
        rooms_q = Q()
        for room in rooms:
            if room == '4':
                rooms_q |= Q(rooms_count__gte=4)
            else:
                rooms_q |= Q(rooms_count=room)
        projects = projects.filter(rooms_q)
    
    # Фильтр по санузлам
    bathrooms = request.GET.getlist('bathrooms')
    if bathrooms:
        baths_q = Q()
        for bath in bathrooms:
            if bath == '3':
                baths_q |= Q(bathrooms_count__gte=3)
            else:
                baths_q |= Q(bathrooms_count=bath)
        projects = projects.filter(baths_q)
    
    # Фильтр по этажности
    floors = request.GET.getlist('floors')
    if floors:
        floors_q = Q()
        for floor in floors:
            if floor == '3':
                floors_q |= Q(floors_count__gte=3)
            else:
                floors_q |= Q(floors_count=floor)
        projects = projects.filter(floors_q)
    # print(area_max, area_min, bathrooms, rooms, floors)
    # Сортировка
    sort = request.GET.get('sort', 'id')
    # projects = projects.order_by(sort)
    # print(len(projects))
    # Пагинация - по 6 проектов на страницу
    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'selected_rooms': request.GET.getlist('rooms'),
        'selected_bathrooms': request.GET.getlist('bathrooms'),
        'selected_floors': request.GET.getlist('floors'),
        'favorites': request.session.get('favorites', []),
    }
    return render(request, 'constructs/home1.html', context)

def catalog_view(request):
    """Отображение каталога с пагинацией по 8 товаров"""
    products = Product.objects.all().prefetch_related('images')
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
    
def product_detail_1(request, product_slug):
    """Страница редактирования проекта"""
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.order_by('order'))
        ),
        slug=product_slug
    )
    id = product.pk
    # Получаем следующий и предыдущий проекты для навигации
    prev_product = Product.objects.filter(
        id__lt=id, 
        is_active=True
    ).order_by('-id').first()
    
    next_product = Product.objects.filter(
        id__gt=id, 
        is_active=True
    ).order_by('id').first()
    
    
    context = {
        'product': product,
        'images': product.images.all(),
        'prev_product': prev_product,
        'next_product': next_product,
        'product_types': ProductType.objects.all(),
        'roof_types': RoofType.objects.all(),
    }
    return render(request, 'constructs/detail.html', context)

@require_POST
def toggle_active(request, product_id):
    """Включение/выключение проекта"""
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save()
    
    # Определяем следующий проект для редиректа
    if not product.is_active:
        next_product = Product.objects.filter(
            id__gt=product_id, 
            is_active=True
        ).order_by('id').first()
        
        if next_product:
            redirect_id = next_product.id
        else:
            prev_product = Product.objects.filter(
                id__lt=product_id, 
                is_active=True
            ).order_by('-id').first()
            redirect_id = prev_product.id if prev_product else None
    else:
        redirect_id = product_id
    
    if redirect_id:
        return JsonResponse({
            'success': True,
            'redirect_url': f'/project/{redirect_id}/'
        })
    else:
        return JsonResponse({
            'success': True,
            'redirect_url': '/catalog/'  # Вернуться в каталог
        })

@require_POST
def set_main_image(request, product_id, image_id):
    """Установка главного изображения"""
    image = get_object_or_404(ProductImage, id=image_id, product_id=product_id)
    
    # Сбрасываем главное у всех
    ProductImage.objects.filter(product_id=product_id).update(is_main=False)
    
    # Устанавливаем новое главное
    image.is_main = True
    image.save()
    
    return JsonResponse({'success': True})

@require_POST
def delete_image(request, product_id, image_id):
    """Удаление изображения"""
    image = get_object_or_404(ProductImage, id=image_id, product_id=product_id)
    image.delete()
    
    # Перенумеровываем порядок
    images = ProductImage.objects.filter(product_id=product_id).order_by('order')
    for idx, img in enumerate(images, 1):
        img.order = idx
        img.save()
    
    return JsonResponse({'success': True})

@require_POST
def reorder_images(request, product_id):
    """Изменение порядка изображений"""
    print(request.POST)
    try:
        # Получаем строку с порядком из POST
        order_string = request.POST.get('order', '')
        
        if not order_string:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан порядок изображений'
            })
        
        # Разбиваем строку на список ID
        image_ids = order_string.split(',')
        
        # Проверяем, что ID не пустые
        image_ids = [id for id in image_ids if id.strip()]
        
        if not image_ids:
            return JsonResponse({
                'success': False, 
                'error': 'Пустой список изображений'
            })
        
        print(f"Получен порядок: {image_ids}")  # Для отладки
        
        # Обновляем порядок для каждого изображения
        for idx, image_id in enumerate(image_ids, 1):
            try:
                ProductImage.objects.filter(
                    id=image_id, 
                    product_id=product_id
                ).update(order=idx)
            except Exception as e:
                print(f"Ошибка обновления изображения {image_id}: {e}")
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })