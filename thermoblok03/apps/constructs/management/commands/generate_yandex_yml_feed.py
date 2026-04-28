# management/commands/generate_yandex_feed.py
from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.base import ContentFile
from pathlib import Path
from apps.constructs.models import Product
from apps.constructs.utils import generate_yandex_yml_feed
from django.conf import settings

class Command(BaseCommand):
    help = 'Генерирует YML фид для Яндекс.Маркета'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Путь для сохранения файла (опционально)'
        )
    
    def handle(self, *args, **options):
        products = Product.objects.filter(is_active=True).order_by("-id")[1:10]
        
        if not products.exists():
            self.stdout.write(self.style.ERROR('Нет активных проектов'))
            return
        
        
        base_url = f'https://thermoblock.ru'
        
        feed_xml = generate_yandex_yml_feed(products, base_url)
        
        if options['output']:
            output_path = Path(options['output'])
            output_path.write_text(feed_xml, encoding='utf-8')
            self.stdout.write(self.style.SUCCESS(f'Фид сохранён в {output_path}'))
        else:
            self.stdout.write(feed_xml)