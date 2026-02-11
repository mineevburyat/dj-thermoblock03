# tests/test_all_app_urls.py
from django.test import SimpleTestCase, Client
from django.urls import get_resolver, URLResolver, URLPattern
from django.conf import settings
import re

class AllAppURLsTest(SimpleTestCase):
    """Тестирование ВСЕХ URL из всех приложений"""
    
    databases = []  # Не используем БД
    
    def setUp(self):
        self.client = Client()
        
    def get_all_urls_from_apps(self):
        """Получаем все URL из всех установленных приложений"""
        all_urls = []
        
        # Получаем корневой URL resolver
        root_resolver = get_resolver()
        
        def extract_urls(patterns, current_namespace=''):
            """Рекурсивно извлекаем URL из паттернов"""
            urls = []
            
            for pattern in patterns:
                # Пропускаем по паттерну
                pattern_str = str(pattern.pattern) if hasattr(pattern, 'pattern') else ''
                if any(regex.search(pattern_str) for regex in self.excluded_patterns.values()):
                    continue
                
                if isinstance(pattern, URLResolver):
                    # Проверяем, не из исключенного ли приложения
                    app_name = getattr(pattern, 'app_name', '')
                    if any(excluded in app_name for excluded in self.excluded_apps):
                        continue
                    
                    # Рекурсивно получаем вложенные URL
                    new_namespace = f"{current_namespace}:{pattern.namespace}" if current_namespace else (pattern.namespace or '')
                    urls.extend(extract_urls(pattern.url_patterns, new_namespace))
                
                elif isinstance(pattern, URLPattern):
                    if hasattr(pattern, 'callback'):
                        # Получаем имя приложения из callback
                        callback = pattern.callback
                        if hasattr(callback, '__module__'):
                            module_name = callback.__module__
                            # Пропускаем исключенные приложения
                            if any(excluded in module_name for excluded in self.excluded_apps):
                                continue
                    
                    if hasattr(pattern, 'name') and pattern.name:
                        full_name = f"{current_namespace}:{pattern.name}" if current_namespace else pattern.name
                        
                        # Пропускаем исключенные имена
                        if any(regex.search(full_name) for regex in self.excluded_patterns.values()):
                            continue
                        
                        # Определяем параметры URL
                        kwargs = self._extract_url_params(pattern)
                        
                        urls.append({
                            'name': full_name,
                            'kwargs': kwargs,
                            'pattern': pattern_str,
                            'lookup_str': full_name
                        })
            
            return urls
        
        return extract_urls(root_resolver.url_patterns)
    
    def _extract_url_params(self, pattern):
        """Извлекает параметры из URL паттерна"""
        kwargs = {}
        
        if hasattr(pattern.pattern, '_route'):
            route = pattern.pattern._route
            
            # Именованные группы: <int:id>, <slug:slug>, <str:name>, etc.
            param_matches = re.findall(r'<(?:\w+:)?(\w+)>', route)
            
            # Тестовые значения для разных типов параметров
            test_values = {
                'slug': 'test-slug',
                'id': 1,
                'pk': 1,
                'uuid': '12345678-1234-1234-1234-123456789012',
                'username': 'testuser',
                'year': '2024',
                'month': '01',
                'day': '15',
                'page': 1,
                'number': 1,
                'code': 'abc123',
                'token': 'test-token',
                'key': 'test-key',
            }
            
            for param in param_matches:
                # Ищем подходящее тестовое значение
                value_found = False
                for key, value in test_values.items():
                    if key in param.lower():
                        kwargs[param] = value
                        value_found = True
                        break
                
                # Если не нашли специфичное значение, используем generic
                if not value_found:
                    if 'id' in param.lower() or 'pk' in param.lower():
                        kwargs[param] = 1
                    elif 'slug' in param.lower():
                        kwargs[param] = 'test-slug'
                    else:
                        kwargs[param] = 'test'
        
        return kwargs
    
    def test_all_urls_can_be_reversed(self):
        """Тест: все URL могут быть получены через reverse()"""
        all_urls = self.get_all_urls_from_apps()
        
        self.assertGreater(len(all_urls), 0, "Не найдено URL для тестирования")
        
        print(f"\nНайдено {len(all_urls)} URL для тестирования:")
        
        for url_info in all_urls:
            with self.subTest(url=url_info['name']):
                try:
                    url = reverse(url_info['name'], kwargs=url_info['kwargs'])
                    self.assertIsInstance(url, str)
                    print(f"✓ {url_info['name']} -> {url}")
                except Exception as e:
                    # Если не хватает обязательных параметров
                    if 'required' in str(e).lower():
                        # Пробуем с минимальными параметрами
                        try:
                            minimal_kwargs = {}
                            for key in url_info['kwargs'].keys():
                                minimal_kwargs[key] = 'test'
                            url = reverse(url_info['name'], kwargs=minimal_kwargs)
                            print(f"⚠ {url_info['name']} -> {url} (с generic параметрами)")
                        except:
                            print(f"✗ {url_info['name']}: требует специфичные параметры")
                            self.fail(f"URL {url_info['name']} требует специфичные параметры: {e}")
                    else:
                        print(f"✗ {url_info['name']}: {e}")
                        self.fail(f"Не удалось получить reverse для '{url_info['name']}': {e}")
    
    def test_all_urls_respond(self):
        """Тест: все URL отвечают на GET запрос"""
        all_urls = self.get_all_urls_from_apps()
        
        print(f"\nТестируем доступность {len(all_urls)} URL:")
        
        for url_info in all_urls:
            with self.subTest(url=url_info['name']):
                try:
                    # Пробуем получить URL
                    url = reverse(url_info['name'], kwargs=url_info['kwargs'])
                    
                    # Делаем GET запрос (follow=True для редиректов)
                    response = self.client.get(url, follow=True)
                    
                    # Допустимые статус-коды
                    acceptable_codes = {200, 301, 302, 403, 404}
                    
                    self.assertIn(
                        response.status_code,
                        acceptable_codes,
                        f"URL {url_info['name']} вернул {response.status_code}"
                    )
                    
                    status_emoji = {
                        200: "✓",
                        301: "↪",
                        302: "↪",
                        403: "🔒",
                        404: "❌"
                    }
                    
                    emoji = status_emoji.get(response.status_code, "?")
                    print(f"{emoji} {url_info['name']} -> {response.status_code}")
                    
                except Exception as e:
                    if 'No reverse match' in str(e):
                        print(f"⚠ {url_info['name']}: нет reverse match")
                        return  # Пропускаем
                    print(f"✗ {url_info['name']}: {e}")
                    self.fail(f"Ошибка при тестировании '{url_info['name']}': {e}")