# management/commands/import_products.py
import os
import json
import shutil
from PIL import Image
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify
from django.conf import settings
from apps.constructs.models import Product, ProductImage, ProductType, RoofType

class Command(BaseCommand):
    help = 'Импорт товаров из JSON файла'
    
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь к JSON файлу с данными')
        parser.add_argument('--images_dir', type=str, help='Директория с изображениями', default=None)
        parser.add_argument('--clear', action='store_true', help='Очистить существующие товары перед импортом')
        parser.add_argument('--min-width', type=int, default=300, 
                          help='Минимальная ширина для оригинала в пикселях (по умолчанию 300)')
        parser.add_argument('--min-height', type=int, default=300,
                          help='Минимальная высота для оригинала в пикселях (по умолчанию 300)')
    def handle(self, *args, **options):
        json_path = options['json_file']
        images_base_dir = options.get('images_dir')
        clear_existing = options['clear']
        min_width = options['min_width']
        min_height = options['min_height']

        self.stdout.write(f'Критерии для оригиналов:')
        self.stdout.write(f'  Минимальная ширина: {min_width}px')
        self.stdout.write(f'  Минимальная высота: {min_height}px')
        # Очистка если нужно
        if clear_existing:
            self.stdout.write('Очистка существующих товаров...')
            Product.objects.all().delete()
            ProductImage.objects.all().delete()
        
        # Загружаем JSON
        self.stdout.write(f'Загрузка данных из {json_path}...')
        with open(json_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        
        # Если images_dir не указан, определяем базовую директорию
        if not images_base_dir:
            # Предполагаем, что JSON лежит в папке data, а изображения в папке images рядом
            json_dir = os.path.dirname(json_path)
            images_base_dir = os.path.join(os.path.dirname(json_dir), 'images')
            # Если такой папки нет, пробуем папку images рядом с JSON
            if not os.path.exists(images_base_dir):
                images_base_dir = os.path.join(json_dir, 'images')
        
        self.stdout.write(f'Базовая директория изображений: {images_base_dir}')
        # Создаем базовые типы товаров (можно вынести в отдельную фикстуру)
        self.create_base_types()
        self.create_roof_types()
                
        # Импортируем товары
        self.import_products(products_data, images_base_dir, min_width, min_height)
        
        self.stdout.write(self.style.SUCCESS(f'Успешно импортировано {len(products_data)} товаров'))
    
    def create_base_types(self):
        """Создает базовые типы товаров"""
        types = [
            {'name': 'Одноэтажные дома', 'slug': '1-story', 'order': 1},
            {'name': 'Полутораэтажные дома', 'slug': '1.5-story', 'order': 2},
            {'name': 'Двухэтажные дома', 'slug': '2-story', 'order': 3},
            {'name': 'Хозпостройки', 'slug': 'outbuilding', 'order': 4},
        ]
        
        for type_data in types:
            ProductType.objects.get_or_create(
                slug=type_data['slug'],
                defaults={'name': type_data['name'], 'order': type_data['order']}
            )
        
        self.stdout.write('Базовые типы товаров созданы')
    
    def create_roof_types(self):
        """Создает базовые типы крыш"""
        roofs = [('Плоская', 'flat_roof'), 
                 ('Вальмовая', 'hipped_roof'), 
                 ('Двускатная', 'gable_roof'),
                 ('Односкатная', 'mono_pitched_roof')]
        
        for roof_name, slug in roofs:
            RoofType.objects.get_or_create(
                slug=slug,
                defaults={'name': roof_name}
            )
        
        self.stdout.write('Базовые типы крыш созданы')

    def is_original_image(self, image_path, min_width, min_height, max_thumb_dim):
        """
        Определяет, является ли файл оригинальным изображением по размерам в пикселях
        Возвращает (is_original, width, height, reason)
        """
        
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                # Проверка на превью (если любой размер меньше или равен max_thumb_dim)
                if width <= max_thumb_dim or height <= max_thumb_dim:
                    return False, width, height, f'Превью ({width}x{height})'
                
                # Проверка минимальных требований к оригиналу
                if width < min_width or height < min_height:
                    return False, width, height, f'Маловат для оригинала ({width}x{height})'
                
                # Проходит все проверки - это оригинал
                return True, width, height, f'ОРИГИНАЛ ({width}x{height})'
                
        except Exception as e:
            return False, 0, 0, f'Ошибка чтения: {e}'

    def find_image_files(self, base_dir, filename_pattern):
        """Ищет все файлы, соответствующие паттерну"""
        matching_files = []
        
        # Ищем во всех поддиректориях
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if filename_pattern in file:
                    full_path = os.path.join(root, file)
                    matching_files.append(full_path)
        
        return matching_files

    def import_products(self, products_data, images_base_dir,  min_width, min_height):
        """Импортирует товары из JSON"""
        max_thumb_dim = 110
        stats = {
            'total': len(products_data),
            'with_images': 0,
            'total_originals': 0,
            'total_thumbnails': 0,
            'skipped_errors': 0
        }
        
        # Статистика по размерам
        size_stats = {
            'small_thumbs': 0,  # <=300px
            'medium': 0,         # 301-800px
            'large': 0,          # 801-1200px
            'xlarge': 0,         # >1200px
            'errors': 0
        }
        for idx, item in enumerate(products_data, 1):
            self.stdout.write(f'Импорт {idx}/{stats["total"]}: {item["title"]}')
            
            # Создаем или обновляем товар
            product, created = Product.objects.update_or_create(
                slug=slugify(item['title']),
                defaults={
                    'title': item['title'],
                    'article': item.get('sku', ''),
                    'description': item.get('description', ''),
                    'short_description': item.get('short_description', '')[:500],
                }
            )
            
            if created:
                self.stdout.write(f'  Создан новый товар')
            else:
                self.stdout.write(f'  Обновлен существующий товар')

            # Ищем изображения для этого товара
            if 'images' in item and item['images']:
                product_stats = self.import_product_images(
                    product, item['images'], images_base_dir, 
                    min_width, min_height, max_thumb_dim
                )
                
                # Обновляем общую статистику
                stats['total_originals'] += product_stats['originals']
                stats['total_thumbnails'] += product_stats['thumbnails']
                stats['skipped_errors'] += product_stats['errors']
                
                size_stats['small_thumbs'] += product_stats['sizes']['small']
                size_stats['medium'] += product_stats['sizes']['medium']
                size_stats['large'] += product_stats['sizes']['large']
                size_stats['xlarge'] += product_stats['sizes']['xlarge']
                size_stats['errors'] += product_stats['sizes']['errors']
                
                if product_stats['originals'] > 0:
                    stats['with_images'] += 1
                    
                self.stdout.write(f'  Найдено оригиналов: {product_stats["originals"]}, '
                                 f'превью: {product_stats["thumbnails"]}')
            else:
                self.stdout.write(self.style.WARNING('  Нет изображений в JSON'))
            

        # Итоговая статистика
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('СТАТИСТИКА ИМПОРТА:'))
        self.stdout.write('='*60)
        self.stdout.write(f'Всего товаров: {stats["total"]}')
        self.stdout.write(f'Товаров с изображениями: {stats["with_images"]}')
        self.stdout.write(f'Загружено оригиналов: {stats["total_originals"]}')
        self.stdout.write(f'Пропущено превью: {stats["total_thumbnails"]}')
        self.stdout.write(f'Ошибок: {stats["skipped_errors"]}')
        
        self.stdout.write('\n' + '-'*60)
        self.stdout.write('РАСПРЕДЕЛЕНИЕ ПО РАЗМЕРАМ:')
        self.stdout.write(f'  Превью (<=300px): {size_stats["small_thumbs"]}')
        self.stdout.write(f'  Средние (301-800px): {size_stats["medium"]}')
        self.stdout.write(f'  Большие (801-1200px): {size_stats["large"]}')
        self.stdout.write(f'  Очень большие (>1200px): {size_stats["xlarge"]}')
        self.stdout.write(f'  Ошибки определения: {size_stats["errors"]}')
        self.stdout.write('='*60)
    
    def import_product_images(self, product, images_data, images_base_dir, 
                             min_width, min_height, max_thumb_dim):
        """Импортирует только оригинальные изображения для товара"""
        stats = {
            'originals': 0,
            'thumbnails': 0,
            'errors': 0,
            'sizes': {
                'small': 0,
                'medium': 0,
                'large': 0,
                'xlarge': 0,
                'errors': 0
            }
        }
        
        # Создаем директорию для товара, если её нет
        product_slug = slugify(product.title)
        
        for order, img_info in enumerate(images_data, 1):
            # Получаем путь к файлу из local_path
            local_path = img_info.get('local_path', '')
            filename = os.path.basename(local_path)
            
            self.stdout.write(f'    [{order}] Поиск: {filename}')
            
            # Ищем файл в разных местах
            found_files = self.find_image_files(images_base_dir, filename)
            
            if not found_files:
                self.stdout.write(self.style.WARNING(f'      Файл не найден'))
                stats['errors'] += 1
                continue
            
            # Берем первый найденный файл
            source_path = found_files[0]
            
            # Определяем, оригинал ли это по размерам
            is_original, width, height, reason = self.is_original_image(
                source_path, min_width, min_height, max_thumb_dim
            )
            
            # Считаем статистику по размерам
            if width > 0:
                max_dim = max(width, height)
                if max_dim <= 300:
                    stats['sizes']['small'] += 1
                elif max_dim <= 800:
                    stats['sizes']['medium'] += 1
                elif max_dim <= 1200:
                    stats['sizes']['large'] += 1
                else:
                    stats['sizes']['xlarge'] += 1
            else:
                stats['sizes']['errors'] += 1
            
            if not is_original:
                self.stdout.write(f'      Пропущен: {reason}')
                stats['thumbnails'] += 1
                continue
            
            self.stdout.write(f'      Найден: {reason}')
            
            try:
                # Проверяем, существует ли уже такое изображение

                
                # Открываем файл
                with open(source_path, 'rb') as f:
                    # Создаем новое изображение
                    image = ProductImage(
                        product=product,
                        order=order,
                        is_main=(order == 1 and stats['originals'] == 0),  # Первый импортированный - главный
                        alt=self.generate_alt(product.title, order, len(images_data))
                    )
                    
                    # Генерируем alt
                    image.alt = f"{product.title} - фото {order}"
                    
                    # Сохраняем файл
                    image.image.save(filename, File(f), save=False)
                    image.save()
                    
                    stats['originals'] += 1
                    self.stdout.write(self.style.SUCCESS(f'      ✅ Импортирован ({width}x{height})'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'      ❌ Ошибка при импорте: {e}'))
                stats['errors'] += 1
        
        return stats

    def guess_product_type(self, product):
        """Пытается определить тип товара по названию"""
        title_lower = product.title.lower()
        # {'name': 'Одноэтажные дома', 'slug': '1-story', 'order': 1},
        # {'name': 'Полутораэтажные дома', 'slug': '1.5-story', 'order': 2},
        # {'name': 'Двухэтажные дома', 'slug': '2-story', 'order': 3},
        # {'name': 'Хозпостройки', 'slug': 'outbuilding', 'order': 4},
        # Определяем тип дома по ключевым словам
        if 'хоз' in title_lower or 'баня' in title_lower or 'гараж' in title_lower:
            product_type = ProductType.objects.filter(slug='outbuilding').first()
        elif '1.5' in title_lower or 'полутор' in title_lower:
            product_type = ProductType.objects.filter(slug='1.5-story').first()
        elif '2' in title_lower or 'двух' in title_lower or 'двухэтажн' in title_lower:
            product_type = ProductType.objects.filter(slug='2-story').first()
        else:
            # По умолчанию считаем одноэтажным
            product_type = ProductType.objects.filter(slug='1-story').first()
        
        if product_type:
            product.product_type = product_type
            product.save(update_fields=['product_type'])
    
    def generate_alt(self, product_title, image_number, total_images):
        """Генерирует alt текст для изображения"""
        # Вариант 1: Простой
        return f"{product_title} - фото {image_number}"


# Дополнительная утилита для ручного заполнения характеристик
class ProductDataUpdater:
    """Класс для обновления характеристик товаров"""
    
    @staticmethod
    def update_product_characteristics(product_id, **kwargs):
        """
        Обновляет характеристики товара
        Пример:
            ProductDataUpdater.update_product_characteristics(
                product_id=1,
                area=150.5,
                rooms_count=5,
                bathrooms_count=2,
                floors_count=2,
                roof_type='Двускатная'
            )
        """
        try:
            product = Product.objects.get(id=product_id)
            
            # Обновляем поля
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            # Если указан тип крыши строкой
            if 'roof_type' in kwargs and isinstance(kwargs['roof_type'], str):
                roof_type, _ = RoofType.objects.get_or_create(
                    name=kwargs['roof_type'],
                    defaults={'slug': slugify(kwargs['roof_type'])}
                )
                product.roof_type = roof_type
            
            product.save()
            return True
            
        except Product.DoesNotExist:
            return False
    
    @staticmethod
    def batch_update_from_csv(csv_path):
        """Массовое обновление из CSV файла"""
        import csv
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                product_id = row.pop('id', None)
                if product_id:
                    ProductDataUpdater.update_product_characteristics(product_id, **row)