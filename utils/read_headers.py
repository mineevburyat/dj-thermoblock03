import requests
from bs4 import BeautifulSoup

# 1. Загрузка страницы
url = 'http://127.0.0.1:8000'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 2. Поиск всех заголовков от h1 до h6
headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

# 3. Анализ и вывод
for header in headers:
    print(f"{header.name}: {header.get_text().strip()}")
