<!-- Дублирование в JSON-LD для футера -->
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": "https://thermoblock.ru/about",
    "name": "ООО Строй Тех",
    "url": "https://thermoblock.ru",
    "logo": "https://thermoblock.ru/static/img/logofull.png",
    "description": "Производитель несъемной бетонной опалубки для строительства энергоэффективных домов",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": ,
        "addressLocality": ,
        "postalCode": ,
        "addressCountry": "RU"
    },
    "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+7-3012-20-63-20",
        "contactType": "customer service",
        "areaServed": "RU",
        "availableLanguage": "Russian"
    },
    
}
</script>

from django.conf import settings

def local_business_schema(request):
    # Базовые данные для всех страниц
    base_schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "legalName": "ООО Строй Тех",
        "name": "ThermoBlock. Термоблок - несъемная бетонная опалубка",
        "description": "Производство блоков несъемной опалубки ThermoBlock и строительство домов под ключ по технологии ThermoBlock",
        "url": request.build_absolute_uri(),
        "telephone": "+7-3012-20-63-20",
        "email": "info@thermoblock.ru",
        "faxNumber": "+7-3012-20-63-20",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "ул. Николая Петрова, д. 70, офис 309",
            "addressLocality": "Улан-Удэ",
            "addressRegion": "Бурятия",
            "postalCode": "670000",
            "addressCountry": "RU"
        },
        # Режим работы
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "09:00",
                "closes": "18:00"
            },
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": "Saturday",
                "opens": "10:00",
                "closes": "17:00"
            }
        ],
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "51.84342112490193",
            "longitude": "107.64706042154886"
        },
        # Логотип и изображения
        "logo": 'https://thermoblock.ru/static/img/logofull.png',
        "sameAs": [
        "https://vk.com/thermoblock",
        "https://t.me/thermoblock",
        "https://www.youtube.com/@thermoblock"
        ],
        # Общая информация
        "foundingDate": "2016-05-15",
        "founder": "Жаргалов Алдар Олегович",
        "numberOfEmployees": "30",
        
    }
    # Добавляем специфику в зависимости от страницы
    path = request.path
    
    if '/blocks/' in path:
        base_schema["additionalType"] = "ManufacturingBusiness"
        base_schema["description"] = "Производство строительных бетонных блоков ThermoBlock для монолитных теплых стен"
        base_schema["hasProductReturnPolicy"] = {
            "@type": "ProductReturnPolicy",
            "productReturnDays": 7,
            }
        
        
    elif '/construction/' in path:
        base_schema["additionalType"] = "HomeAndConstructionBusiness"
        base_schema["description"] = "Строительство домов под ключ по технологии ThermoBlock"
        
    elif '/services/' in path:
        base_schema["additionalType"] = "ProfessionalService"
        base_schema["description"] = "Строительные услуги"
    
    return {'local_business_schema': base_schema}