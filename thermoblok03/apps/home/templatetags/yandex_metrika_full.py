from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import json

# Регистрируем тег
register = template.Library()

# Создаем простой тег
@register.simple_tag
def yandex_metrika(force=False):
    """
    Возвращает код Яндекс.Метрики.
    Номер счетчика берется из настроек.
    """
    # Не показываем в debug режиме, если не указано force=True
    if settings.DEBUG and not force:
        return mark_safe('<!-- Яндекс.Метрика отключена в debug режиме -->')
    # Получаем номер счетчика из настроек
    counter_id = getattr(settings, 'YANDEX_METRIKA_ID', None)
    
    # Если счетчик не настроен - ничего не выводим
    if not counter_id:
        return ''
    
    config = getattr(settings, 'YANDEX_METRIKA_CONFIG', {
        'clickmap': True,
        'trackLinks': True,
        'accurateTrackBounce': True,
        'webvisor': True,
    })
    config_json = json.dumps(config, ensure_ascii=False)
    code = f'''
        <!-- Yandex.Metrika counter -->
        <script type="text/javascript">
            (function(m,e,t,r,i,k,a){{
                m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
                m[i].l=1*new Date();
                for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
                k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
            }})(window, document,"script","https://mc.yandex.ru/metrika/tag.js", "ym");

            ym({counter_id}, "init", {config_json});
            // Добавляем глобальную функцию для удобства
            window.sendYandexGoal = function(goalName, params) {{
                if (params) {{
                ym({counter_id}, 'reachGoal', goalName, params);
                }} else {{
                ym({counter_id}, 'reachGoal', goalName);
                }}
            }};
        </script>
        <noscript><div><img src="https://mc.yandex.ru/watch/{counter_id}" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
        <!-- /Yandex.Metrika counter -->
    '''
    return mark_safe(code)

@register.simple_tag
def ym_goal(goal_name, *params):
    """
    Теперь использует нашу глобальную функцию
    """
    if params:
        params_str = ', '.join([f"'{p}'" for p in params])
        return mark_safe(f"sendYandexGoal('{goal_name}', [{params_str}])")
    else:
        return mark_safe(f"sendYandexGoal('{goal_name}')")

# Дополнительные удобные теги
@register.simple_tag
def ym_data_goal(goal_name):
    """
    Тег для data-атрибутов
    """
    return mark_safe(f'data-ym-goal="{goal_name}"')

@register.simple_tag
def ym_auto_goals(force=False):
    """
    Автоматически добавляет обработку data-атрибутов
    """
    if settings.DEBUG and not force:
        return mark_safe('<!-- Яндекс.Метрика отключена в debug режиме -->')
    
    return mark_safe("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Обработка кнопок с data-ym-goal
        document.querySelectorAll('[data-ym-goal]').forEach(function(element) {
            element.addEventListener('click', function() {
                var goalName = this.getAttribute('data-ym-goal');
                if (window.sendYandexGoal) {
                    window.sendYandexGoal(goalName);
                }
            });
        });
        
        // Автоотслеживание форм
        document.querySelectorAll('form').forEach(function(form) {
            form.addEventListener('submit', function() {
                var formId = this.id || this.name || 'unknown_form';
                if (window.sendYandexGoal) {
                    window.sendYandexGoal('form_submit_' + formId);
                }
            });
        });
    });
    </script>
    """)