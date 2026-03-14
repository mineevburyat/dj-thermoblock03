# serializers.py

from rest_framework import serializers
from .models import District, House, HouseMedia, Review

class HouseMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = HouseMedia
        fields = ['id', 'media_type', 'file_url', 'video_url', 'title', 
                  'description', 'is_primary', 'sort_order']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None


class ReviewSerializer(serializers.ModelSerializer):
    house_name = serializers.CharField(source='house.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'house', 'house_name', 'author_name', 'rating', 
                  'text', 'response_text', 'response_date', 'created_at']
        read_only_fields = ['response_date', 'created_at']


class HouseDetailSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    media = HouseMediaSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    reviews_count = serializers.IntegerField(source='reviews.count', read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = House
        fields = ['id', 'name', 'district', 'district_name', 'description', 
                  'address', 'latitude', 'longitude', 'built_year', 'area_sqm',
                  'floors', 'price', 'status', 'features', 'media', 'reviews',
                  'reviews_count', 'average_rating', 'created_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_published=True)
        if reviews.exists():
            return round(reviews.aggregate(avg=models.Avg('rating'))['avg'], 1)
        return None


class HouseListSerializer(serializers.ModelSerializer):
    """Компактный сериализатор для списка домов"""
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = House
        fields = ['id', 'name', 'district_id', 'address', 'area_sqm', 
                  'price', 'status', 'primary_image']
    
    def get_primary_image(self, obj):
        primary = obj.media.filter(is_primary=True).first()
        if primary and primary.file:
            return primary.file.url
        # Если нет главного, берем первое изображение
        first_image = obj.media.filter(media_type='image').first()
        if first_image and first_image.file:
            return first_image.file.url
        return None


class DistrictSerializer(serializers.ModelSerializer):
    houses_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'center_latitude', 'center_longitude', 
                  'boundary_geojson', 'houses_count']


class DistrictDetailSerializer(serializers.ModelSerializer):
    houses = HouseListSerializer(many=True, read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'description', 'center_latitude', 
                  'center_longitude', 'boundary_geojson', 'houses_count', 'houses']