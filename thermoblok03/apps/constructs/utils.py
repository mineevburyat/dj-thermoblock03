# apps/constructs/utils.py
import os
from django.utils import timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def generate_yandex_yml_feed(products, base_url):
    """
    Генерирует YML фид для Яндекс.Маркета / Яндекс.Недвижимости
    """
    
    # Корневой элемент
    yml_catalog = Element('yml_catalog')
    yml_catalog.set('date', timezone.now().strftime('%Y-%m-%d %H:%M'))
    
    # Элемент shop
    shop = SubElement(yml_catalog, 'shop')
    
    # Основная информация о магазине
    name = SubElement(shop, 'name')
    name.text = 'ThermoBlock'
    
    company = SubElement(shop, 'company')
    company.text = 'ООО "Строй Тех"'
    
    url = SubElement(shop, 'url')
    url.text = base_url + '/'
    
    platform = SubElement(shop, 'platform')
    platform.text = 'Django'
    """
    <currencies>
      <currency id="RUB" rate="1"/>
    </currencies>
    <sets>
      <set id="s1">
      <name>Домокомплекты ThermoBlock</name>
      <url>https://thermoblock.ru/constructs/</url>
      </set>
    </sets>
    <categories>
      <category id="1">Одноэтажные дома из ThermoBlock</category>
      <category id="3">Двухэтажные дома из ThermoBlock</category>
      <category id="4">Усадебный комплекс из ThermoBlock</category>
    </categories>
    """
    # Валюта
    currencies = SubElement(shop, 'currencies')
    currency = SubElement(currencies, 'currency')
    currency.set('id', 'RUB')
    currency.set('rate', '1')
    
    # Сет
    sets = SubElement(shop, 'sets')
    y_set = SubElement(sets, 'set')
    y_set.set('id', 'setThermoBlock1')
    y_set.set('url', 'https://thermoblock.ru/constructs/')
    # Категории
    categories = SubElement(shop, 'categories')
    categories_dict = {}
    
    for product in products:
        if product.product_type and product.product_type.id not in categories_dict:
            cat_elem = SubElement(categories, 'category')
            cat_elem.set('id', str(product.product_type.id))
            cat_elem.text = product.product_type.name
            categories_dict[product.product_type.id] = True
    
    # Основной блок с товарами
    offers = SubElement(shop, 'offers')
    """
    <offer id="2208" available="true" type="vendor.model">
        <url>https://thermoblock.ru/constructs/eravna-108/</url>
        <price>0</price>
        <currencyId>RUB</currencyId>
        <categoryId>1</categoryId>
        <picture>https://thermoblock.ru/media/constructs/eravna_vecher.webp</picture>
        <picture>https://thermoblock.ru/media/constructs/eravna_utro.webp</picture>
        <picture>https://thermoblock.ru/media/constructs/eravna_common.webp</picture>
        <picture>https://thermoblock.ru/media/constructs/eravna_back.webp</picture>
        <picture>https://thermoblock.ru/media/constructs/eravna_fasad.jpg</picture>
        <picture>https://thermoblock.ru/media/constructs/eravna_mebel.jpg</picture>
        <picture>https://thermoblock.ru/media/constructs/eravna_size.jpg</picture>
        <name>Еравна 108</name>
        <description>«Еравна-108»: дом из ThermoBlock — быстро, тепло, технологично. Спальня, большая детская, раздельные кухня и гостиная, санузел, котельная. Тёплые полы.</description>
        <vendor>ThermoBlock</vendor>
        <model>eravna-12-9-1</model>
        <params>
          <param name="Площадь">108.0 м²</param>
          <param name="Количество комнат">3</param>
          <param name="Количество спален">2</param>
          <param name="Количество санузлов">1</param>
          <param name="Тип строения">Одноэтажные дома</param>
          <param name="Тип крыши">Двускатная</param>
        </params>
      </offer>
    """
    for product in products:
        # Создаём offer
        offer = SubElement(offers, 'offer')
        offer.set('id', f'thermoblock{str(product.id)}')
        offer.set('available', 'true')
        offer.set('type', 'vendor.model')
        
        # URL страницы товара
        product_url = SubElement(offer, 'url')
        product_url.text = f'{base_url}{product.get_absolute_url()}'
        
        # Цена
        price = SubElement(offer, 'price')
        # Если есть поле price, используйте его, иначе 0
        price.text = str(int(product.price)) if hasattr(product, 'price') and product.price else '0'
        
        # Валюта
        currency_id = SubElement(offer, 'currencyId')
        currency_id.text = 'RUB'
        
        # Категория
        category_id_elem = SubElement(offer, 'categoryId')
        if product.product_type:
            category_id_elem.text = str(product.product_type.id)
        else:
            category_id_elem.text = '1'
        
        # Изображения
        pictures = product.images.all()
        for picture in pictures:
            picture_elem = SubElement(offer, 'picture')
            if hasattr(picture, 'image') and picture.image:
                picture_elem.text = f'{base_url}{picture.image.url}'
        
        # Название
        name_elem = SubElement(offer, 'name')
        name_elem.text = product.title
        
        # Описание
        description = SubElement(offer, 'description')
        description.text = product.short_description or product.description or f'Проект {product.title} из термоблока'
        
        # Вендор и модель
        vendor = SubElement(offer, 'vendor')
        vendor.text = 'ThermoBlock'
        
        model = SubElement(offer, 'model')
        model.text = product.article or product.slug.upper()
        
        # Дополнительные параметры
        params = SubElement(offer, 'params')
        
        if product.area:
            param = SubElement(params, 'param')
            param.set('name', 'Площадь')
            param.text = f'{float(product.area):.1f} м²'
        
        if product.rooms_count:
            param = SubElement(params, 'param')
            param.set('name', 'Количество комнат')
            param.text = str(product.rooms_count)
        
        if product.bedrooms_count:
            param = SubElement(params, 'param')
            param.set('name', 'Количество спален')
            param.text = str(product.bedrooms_count)
        
        if product.bathrooms_count:
            param = SubElement(params, 'param')
            param.set('name', 'Количество санузлов')
            param.text = str(product.bathrooms_count)
        
        if product.garage:
            param = SubElement(params, 'param')
            param.set('name', 'Гараж')
            param.text = 'есть'
        
        if product.terrace:
            param = SubElement(params, 'param')
            param.set('name', 'Терраса')
            param.text = 'есть'
        
        if product.product_type:
            param = SubElement(params, 'param')
            param.set('name', 'Тип строения')
            param.text = product.product_type.name
        
        if product.roof_type:
            param = SubElement(params, 'param')
            param.set('name', 'Тип крыши')
            param.text = product.roof_type.name
    
    # КРИТИЧЕСКИ ВАЖНО: убираем все пробелы и переносы до XML-декларации
    xml_str = tostring(yml_catalog, encoding='unicode')
    print(xml_str[:40])
    # Форматируем без лишних пробелов в начале
    dom = minidom.parseString(xml_str.encode('utf-8'))
    pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
    
    # Удаляем пустые строки и пробелы в начале
    lines = pretty_xml.split('\n')
    # Находим первую непустую строку (должна быть <?xml)
    start_index = 0
    for i, line in enumerate(lines):
        if line.strip():
            start_index = i
            break
    
    cleaned_xml = '\n'.join(lines[start_index:])
    
    # Возвращаем чистый XML
    return cleaned_xml