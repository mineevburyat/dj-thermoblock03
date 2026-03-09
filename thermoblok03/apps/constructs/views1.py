# views.py
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, ProductType
from django.shortcuts import render, get_object_or_404, redirect

def project_list(request):
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
    return render(request, 'constructs/home1.html', context)