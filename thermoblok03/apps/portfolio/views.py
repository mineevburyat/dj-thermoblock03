from django.shortcuts import render
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
