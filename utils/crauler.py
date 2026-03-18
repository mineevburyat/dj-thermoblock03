import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_valid_link(url, base_domain):
    # Исключаем медиа-файлы и документы
    exclude_ext = ('.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.mp4', '.svg', '.webp')
    parsed = urlparse(url)
    
    # Ссылка должна быть того же домена и не быть файлом
    return (parsed.netloc == base_domain and 
            not parsed.path.lower().endswith(exclude_ext))

def crawl_site(start_url, max_pages=20):
    base_domain = urlparse(start_url).netloc
    visited = set()
    to_visit = [start_url]
    results = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        
        # Убираем якоря (#), чтобы не обходить одну страницу дважды
        clean_url = url.split('#')[0].rstrip('/')
        if clean_url in visited:
            continue
            
        try:
            response = requests.get(clean_url, timeout=5)
            visited.add(clean_url)
            
            # Проверяем, что это именно HTML-страница, а не бинарный файл
            if 'text/html' not in response.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Парсим SEO данные
            page_data = {
                "url": clean_url,
                "title": soup.title.string.strip() if soup.title else "N/A",
                "description": "N/A",
                "keywords": "N/A"
            }

            for meta in soup.find_all("meta"):
                name = meta.get("name", "").lower()
                if name == "description":
                    page_data["description"] = meta.get("content", "").strip()
                if name == "keywords":
                    page_data["keywords"] = meta.get("content", "").strip()

            results.append(page_data)

            # Собираем новые ссылки
            for link in soup.find_all('a', href=True):
                full_url = urljoin(clean_url, link['href'])
                if is_valid_link(full_url, base_domain) and full_url not in visited:
                    to_visit.append(full_url)

        except Exception as e:
            print(f"Ошибка на {clean_url}: {e}")

    return results

# Тест
data = crawl_site("http://127.0.0.1:8000") # Замените на нужный сайт
for p in data:
    print(f"URL: {p['url']}\nTITLE: {p['title']}\nDESC: {p['description']}\n")