# management/commands/import_products.py
import os
import json
import shutil
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
    
    def handle(self, *args, **options):
        json_path = options['json_file']
        images_base_dir = options.get('images_dir')
        clear_existing = options['clear']
        
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
        
        # Создаем базовые типы товаров (можно вынести в отдельную фикстуру)
        self.create_base_types()
        self.create_roof_types()
                
        # Импортируем товары
        self.import_products(products_data, images_base_dir)
        
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

    def import_products(self, products_data, images_base_dir):
        """Импортирует товары из JSON"""
        for idx, item in enumerate(products_data, 1):
            self.stdout.write(f'Импорт {idx}/{len(products_data)}: {item["title"]}')
            
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

            # Пытаемся определить тип товара из названия
            self.guess_product_type(product)

            # Импортируем изображения
            if 'images' in item and item['images']:
                self.import_product_images(product, item['images'], images_base_dir)
            else:
                self.stdout.write(self.style.WARNING('  Нет изображений для импорта'))
            
            
            # Генерируем alt для изображений если их нет
            self.update_images_alt(product)
    
    def import_product_images(self, product, images_data, images_base_dir):
        """Импортирует изображения для товара"""
        imported_count = 0
        
        for order, img_info in enumerate(images_data, 1):
            # Получаем путь к изображению из local_path
            local_path = img_info.get('local_path')
            if not local_path:
                self.stdout.write(self.style.WARNING(f'    Нет local_path для изображения {order}'))
                continue
            
            # Формируем полный путь к файлу
            # Если local_path уже абсолютный, используем его
            if os.path.isabs(local_path):
                source_path = local_path
            else:
                # Иначе ищем относительно базовой директории
                source_path = os.path.join(images_base_dir, local_path)
            
            # Также пробуем искать просто имя файла в базовой директории
            filename = os.path.basename(local_path)
            alt_source_path = os.path.join(images_base_dir, filename)
            
            # Проверяем существование файла
            if os.path.exists(source_path):
                final_source_path = source_path
            elif os.path.exists(alt_source_path):
                final_source_path = alt_source_path
                self.stdout.write(f'    Найден файл по имени: {alt_source_path}')
            else:
                self.stdout.write(self.style.WARNING(f'    Файл не найден:\n      {source_path}\n      {alt_source_path}'))
                continue
            
            self.stdout.write(f'    Импорт изображения {order}: {filename}')
            
            # Открываем файл и сохраняем в модель
            try:
                with open(final_source_path, 'rb') as f:
                    # Создаем новое изображение
                    image = ProductImage(
                        product=product,
                        order=order,
                        is_main=(order == 1)  # Первое изображение - главное
                    )
                    
                    # Сохраняем файл с уникальным именем в media
                    # Django сам создаст уникальное имя если файл с таким именем уже есть
                    image.image.save(filename, File(f), save=False)
                    image.save()
                    
                    imported_count += 1
                    self.stdout.write(self.style.SUCCESS(f'      Импортировано'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'      Ошибка при импорте: {e}'))
        
        self.stdout.write(f'  Импортировано изображений: {imported_count}/{len(images_data)}')
    
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
    
    def update_images_alt(self, product):
        """Обновляет alt текст для всех изображений товара"""
        for idx, image in enumerate(product.images.all(), 1):
            if not image.alt:
                image.alt = f"{product.title} - фото {idx}"
                image.save(update_fields=['alt'])


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