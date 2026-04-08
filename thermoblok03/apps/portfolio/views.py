from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import District, House, Review
from .serializers import (
    DistrictSerializer, DistrictDetailSerializer,
    HouseListSerializer, HouseDetailSerializer,
    ReviewSerializer
)
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
from .models import District, House, Review
from django.http import JsonResponse

class IndexView(TemplateView):
    template_name = 'portfolio/index_geo.html'

class Portfolio(TemplateView):
    """Главная страница"""
    template_name = 'old/portfolio.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["portfolioData"] = {
                1: {
                    'title': "Уютный дом в скандинавском стиле",
                    'description': "Полное описание проекта. Здесь можно рассказать об особенностях планировки, использованных материалах и сроках строительства. Дом построен для семьи с двумя детьми.",
                    'price': "5 500 000 ₽",
                    'area': "143 м²",
                    'images': [
                        "/media/portfolio/dom1-render.webp",
                        "/media/portfolio/dom1-profil.webp",
                        "/media/portfolio/dom1-plan1.webp",
                        "/media/portfolio/dom1-kitchen.webp",
                        "/media/portfolio/dom1-hol.webp",
                    ]
                },
                2: {
                    'title': "Современный дом с террасой",
                    'description': "Описание второго проекта. Просторный дом для загородного проживания. Большая остекленная терраса и второй свет в гостиной.",
                    'price': "7 200 000 ₽",
                    'area': "168 м²",
                    'images': [
                        "/media/portfolio/dom2-render.webp",
                        "/media/portfolio/dom2-profil.webp",
                    ]
                },
                3: {
                    'title': "Современный дом с террасой",
                    'description': "Описание третьего проекта. Просторный дом для загородного проживания. Большая остекленная терраса и второй свет в гостиной.",
                    'price': "7 200 000 ₽",
                    'area': "168 м²",
                    'images': [
                        "/media/portfolio/dom3-render.webp",
                        "/media/portfolio/dom3-profil.webp",
                    ]
                }
            }
        return context
    
class DistrictViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с районами
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DistrictDetailSerializer
        return DistrictSerializer
    
    @action(detail=True, methods=['get'])
    def houses(self, request, pk=None):
        """Получить все дома в районе"""
        district = self.get_object()
        houses = district.houses.all()
        
        # Фильтрация по статусу
        status = request.query_params.get('status')
        if status:
            houses = houses.filter(status=status)
        
        page = self.paginate_queryset(houses)
        if page is not None:
            serializer = HouseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HouseListSerializer(houses, many=True)
        return Response(serializer.data)


class HouseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с домами
    """
    queryset = House.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'address']
    filterset_fields = ['district', 'status', 'built_year']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HouseListSerializer
        return HouseDetailSerializer
    
    def get_queryset(self):
        queryset = House.objects.all()
        
        # Аннотации для списка
        if self.action == 'list':
            queryset = queryset.annotate(
                reviews_count=Count('reviews', filter=Q(reviews__is_published=True)),
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_published=True))
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Получить все отзывы к дому"""
        house = self.get_object()
        reviews = house.reviews.filter(is_published=True)
        
        # Сортировка
        ordering = request.query_params.get('ordering', '-created_at')
        reviews = reviews.order_by(ordering)
        
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        """Добавить отзыв к дому"""
        house = self.get_object()
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(house=house)
            
            # Обновляем средний рейтинг (можно через сигнал или кэш)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с отзывами
    """
    queryset = Review.objects.filter(is_published=True)
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['house', 'rating', 'is_published']
    
    @action(detail=True, methods=['post'])
    def add_response(self, request, pk=None):
        """Добавить ответ на отзыв"""
        review = self.get_object()
        
        response_text = request.data.get('response_text')
        if not response_text:
            return Response(
                {'error': 'Текст ответа обязателен'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review.response_text = response_text
        review.save()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)



def index(request):
    """
    Главная страница с картой, отзывами и портфолио
    """
    # Получаем последние отзывы с пагинацией
    reviews_list = Review.objects.filter(
        is_published=True
    ).select_related('house').order_by('-created_at')
    
    reviews_paginator = Paginator(reviews_list, 3)  # 3 отзыва на странице
    reviews_page = request.GET.get('reviews_page', 1)
    reviews = reviews_paginator.get_page(reviews_page)
    
    # Получаем дома с аннотациями
    houses_list = House.objects.filter(
        status='built'
    ).select_related('district').annotate(
        reviews_count=Count('reviews', filter=Q(reviews__is_published=True)),
        average_rating=Avg('reviews__rating', filter=Q(reviews__is_published=True))
    ).order_by('-created_at')
    
    houses_paginator = Paginator(houses_list, 5)  # 5 домов на странице
    houses_page = request.GET.get('houses_page', 1)
    houses = houses_paginator.get_page(houses_page)
    
    context = {
        'reviews': reviews,
        'houses': houses,
    }
    return render(request, 'portfolio/index_geo1.html', context)


def reviews_list(request):
    """AJAX view для пагинации отзывов"""
    reviews_list = Review.objects.filter(
        is_published=True
    ).select_related('house').order_by('-created_at')
    
    paginator = Paginator(reviews_list, 3)
    page = request.GET.get('page', 1)
    reviews = paginator.get_page(page)
    
    return render(request, 'includes/reviews_list.html', {'reviews': reviews})


def houses_list(request):
    """AJAX view для пагинации домов"""
    houses_list = House.objects.filter(
        status='built'
    ).select_related('district').annotate(
        reviews_count=Count('reviews', filter=Q(reviews__is_published=True)),
        average_rating=Avg('reviews__rating', filter=Q(reviews__is_published=True))
    ).order_by('-created_at')
    
    paginator = Paginator(houses_list, 5)
    page = request.GET.get('page', 1)
    houses = paginator.get_page(page)
    
    return render(request, 'includes/houses_list.html', {'houses': houses})

def house_detail(request, pk):
    """Детальная страница дома"""
    house = get_object_or_404(
        House.objects.select_related('district').prefetch_related(
            'media',
            'reviews'
        ),
        pk=pk
    )
    
    reviews = house.reviews.filter(is_published=True).order_by('-created_at')
    
    # Средний рейтинг
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    
    context = {
        'house': house,
        'reviews': reviews,
        'average_rating': average_rating,
        'yandex_api_key': 'ваш_API_ключ',  # из настроек
    }
    return render(request, 'portfolio/house_detail.html', context)


def review_detail(request, pk):
    """Детальная страница отзыва"""
    review = get_object_or_404(
        Review.objects.select_related('house__district').prefetch_related('photos'),
        pk=pk,
        is_published=True
    )
    
    context = {
        'review': review,
    }
    return render(request, 'portfolio/review_detail.html', context)


def house_list(request):
    """Список всех домов с фильтрацией"""
    houses = House.objects.select_related('district').prefetch_related(
        'media'
    ).annotate(
        reviews_count=Count('reviews', filter=Q(reviews__is_published=True)),
        average_rating=Avg('reviews__rating', filter=Q(reviews__is_published=True))
    )
    
    # Фильтрация
    district_id = request.GET.get('district')
    if district_id:
        houses = houses.filter(district_id=district_id)
    
    status = request.GET.get('status')
    if status:
        houses = houses.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        houses = houses.filter(
            Q(name__icontains=search) | Q(address__icontains=search)
        )
    
    # Сортировка
    sort = request.GET.get('sort', '-created_at')
    houses = houses.order_by(sort)
    
    # Пагинация
    paginator = Paginator(houses, 12)  # 12 домов на страницу
    page = request.GET.get('page', 1)
    houses_page = paginator.get_page(page)
    
    # Для фильтров
    districts = District.objects.all()
    
    context = {
        'houses': houses_page,
        'paginator': paginator,
        'districts': districts,
    }
    return render(request, 'portfolio/house_list.html', context)


def review_list(request):
    """Список всех отзывов с фильтрацией"""
    reviews = Review.objects.filter(
        is_published=True
    ).select_related(
        'house__district'
    ).prefetch_related(
        'photos'
    )
    
    # Фильтрация по рейтингу
    rating = request.GET.get('rating')
    if rating and rating != 'all':
        reviews = reviews.filter(rating=rating)
    
    # Сортировка
    sort = request.GET.get('sort', 'newest')
    if sort == 'newest':
        reviews = reviews.order_by('-created_at')
    elif sort == 'oldest':
        reviews = reviews.order_by('created_at')
    elif sort == 'highest':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort == 'lowest':
        reviews = reviews.order_by('rating', '-created_at')
    
    # Пагинация
    paginator = Paginator(reviews, 10)  # 10 отзывов на страницу
    page = request.GET.get('page', 1)
    reviews_page = paginator.get_page(page)
    
    # Статистика
    total_reviews = Review.objects.filter(is_published=True).count()
    average_rating = Review.objects.filter(
        is_published=True
    ).aggregate(avg=Avg('rating'))['avg']
    total_houses_with_reviews = Review.objects.filter(
        is_published=True
    ).values('house').distinct().count()
    
    context = {
        'reviews': reviews_page,
        'paginator': paginator,
        'total_reviews': total_reviews,
        'average_rating': average_rating,
        'total_houses_with_reviews': total_houses_with_reviews,
    }
    return render(request, 'portfolio/review_list.html', context)


def district_detail(request, pk):
    """Детальная страница района"""
    district = get_object_or_404(District, pk=pk)
    
    houses = district.houses.filter(
        status='built'
    ).annotate(
        reviews_count=Count('reviews', filter=Q(reviews__is_published=True)),
        average_rating=Avg('reviews__rating', filter=Q(reviews__is_published=True))
    )[:6]
    
    context = {
        'district': district,
        'houses': houses,
        'yandex_api_key': 'ваш_API_ключ',
    }
    return render(request, 'portfolio/district_detail.html', context)

def districts_api(request):
    """API для получения данных районов для карты"""
    districts = District.objects.annotate(
        houses_count=Count('houses', filter=Q(houses__status='built'))
    ).values('id', 'name', 'center_latitude', 'center_longitude', 'houses_count')
    
    return JsonResponse(list(districts), safe=False)

def portfolio_view(request):
    houses = House.objects.all()
    context = {
        'houses': houses,
        'total_count': houses.count(),
    }
    return render(request, 'portfolio/section_portfolio.html', context)