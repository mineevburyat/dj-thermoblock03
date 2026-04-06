# views.py
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, ProductType, ProductImage, RoofType
from django.db.models import Prefetch, Max
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

def product_list(request):
    projects = Product.objects.filter(is_active=True)
    
    # Фильтр по площади
    area_min = request.GET.get('area_min')
    area_max = request.GET.get('area_max')
    if area_min:
        projects = projects.filter(area__gte=area_min)
    if area_max:
        projects = projects.filter(area__lte=area_max)
    
    # Фильтр по комнатам (радио)
    rooms = request.GET.get('rooms')
    if rooms:
        if rooms == '4':
            projects = projects.filter(rooms_count__gte=4)
        else:
            projects = projects.filter(rooms_count=rooms)
    
    # Фильтр по спальням (радио)
    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        if bedrooms == '4':
            projects = projects.filter(bedrooms_count__gte=4)
        else:
            projects = projects.filter(bedrooms_count=bedrooms)
    
    # Фильтр по санузлам (радио)
    bathrooms = request.GET.get('bathrooms')
    if bathrooms:
        if bathrooms == '3':
            projects = projects.filter(bathrooms_count__gte=3)
        else:
            projects = projects.filter(bathrooms_count=bathrooms)
    
    # Фильтр по типу строения (этажность)
    product_type = request.GET.get('product_type')
    if product_type:
        projects = projects.filter(product_type_id=product_type)
    
    # Фильтр по дополнительным опциям
    if request.GET.get('garage'):
        projects = projects.filter(garage=True)
    
    if request.GET.get('terrace'):
        projects = projects.filter(terrace=True)
    
    # Сортировка
    sort = request.GET.get('sort', '-created_at')
    # projects = projects.order_by(sort)
    
    # Пагинация
    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'product_types': ProductType.objects.all(),
        'selected_rooms': request.GET.get('rooms', ''),
        'selected_bedrooms': request.GET.get('bedrooms', ''),
        'selected_bathrooms': request.GET.get('bathrooms', ''),
        'selected_type': request.GET.get('product_type', ''),
        'favorites': request.session.get('favorites', []),
    }
    return render(request, 'constructs/index.html', context)

def product_detail(request, slug):
    """Детальная страница проекта"""
    product = get_object_or_404(
        Product.objects.prefetch_related('images'),
        slug=slug,
        is_active=True
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
    # Похожие проекты (по тому же типу)
    similar_products = Product.objects.filter(
        product_type=product.product_type,
        is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]
    
    # Форматирование характеристик для отображения
    characteristics = []
    
    if product.area:
        characteristics.append({
            'icon': '📐',
            'label': 'Площадь',
            'value': f'{product.area} м²'
        })
    
    if product.floors_count:
        value = f'{product.floors_count()} этажа'
        characteristics.append({
            'icon': '🏗️',
            'label': 'Этажность',
            'value': value
        })
    
    if product.rooms_count:
        characteristics.append({
            'icon': '🛋️',
            'label': 'Комнат',
            'value': product.rooms_count
        })
    
    if product.bedrooms_count:
        characteristics.append({
            'icon': '🛏️',
            'label': 'Спален',
            'value': product.bedrooms_count
        })
    
    if product.bathrooms_count:
        characteristics.append({
            'icon': '🚿',
            'label': 'Санузлов',
            'value': product.bathrooms_count
        })
    
    if product.roof_type:
        characteristics.append({
            'icon': '🏠',
            'label': 'Крыша',
            'value': product.roof_type.name
        })
    
    context = {
        # 'product': product,
        'project': product,
        # 'images': product.images.all().order_by('order'),
        'project_images': product.images.all().order_by('order'),
        'characteristics': characteristics,
        'similar_products': similar_products,
        'prev_product': prev_product,
        'next_product': next_product,
    }
    return render(request, 'constructs/detail_new.html', context)

def product_edit(request, product_id):
    """Страница редактирования проекта"""
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.order_by('order'))
        ),
        id=product_id
    )
    
    # Получаем следующий и предыдущий проекты для навигации
    prev_product = Product.objects.filter(
        id__lt=product_id, 
        is_active=True
    ).order_by('-id').first()
    
    next_product = Product.objects.filter(
        id__gt=product_id, 
        is_active=True
    ).order_by('id').first()
    
    if request.method == 'POST':
        # Обновляем основные поля
        product.title = request.POST.get('title')
        product.article = request.POST.get('article')
        product.description = request.POST.get('description')
        product.short_description = request.POST.get('short_description')
        
        # Типы
        product_type_id = request.POST.get('product_type')
        product.product_type_id = product_type_id if product_type_id else None
        
        roof_type_id = request.POST.get('roof_type')
        product.roof_type_id = roof_type_id if roof_type_id else None
        
        # Характеристики
        product.area = request.POST.get('area') or None
        product.floors_count = request.POST.get('floors_count') or None
        product.rooms_count = request.POST.get('rooms_count') or None
        product.bedrooms_count = request.POST.get('bedrooms_count') or None
        product.bathrooms_count = request.POST.get('bathrooms_count') or None
        
        # Булевы поля
        product.garage = request.POST.get('garage') == 'on'
        product.terrace = request.POST.get('terrace') == 'on'
        
        # Статусы
        product.is_active = request.POST.get('is_active') == 'on'
        product.is_popular = request.POST.get('is_popular') == 'on'
        product.is_new = request.POST.get('is_new') == 'on'
        
        product.save()
        
        # Обработка новых изображений
        if request.FILES.getlist('new_images'):
            max_order = product.images.aggregate(Max('order'))['order__max'] or 0
            
            for idx, image_file in enumerate(request.FILES.getlist('new_images')):
                ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    order=max_order + idx + 1,
                    alt=f"{product.title} - фото {max_order + idx + 1}"
                )
        
        messages.success(request, 'Проект успешно обновлен')
        return redirect('constructs:product-edit', product_id=product.id)
    
    context = {
        'product': product,
        'images': product.images.all(),
        'prev_product': prev_product,
        'next_product': next_product,
        'product_types': ProductType.objects.all(),
        'roof_types': RoofType.objects.all(),
    }
    return render(request, 'constructs/edit_detail.html', context)