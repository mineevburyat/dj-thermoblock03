from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from .forms import FeedbackForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .forms import CalculationRequestForm
from django.core.mail import send_mail
from django.conf import settings

from django.views.generic import TemplateView

import json
from datetime import datetime

import bitrix24
# TODO make capcha

def create_on_crm(instanse, name, phone, description=''):
    bx = bitrix24.Bitrix24('https://b24-h4z6cg.bitrix24.ru/rest/1/voeqwkq3jrdf6sp1/')
    crm_status = True
    crm_error = ''
    try:
        contact_id = bx.callMethod('crm.contact.add', 
                                   fields={"NAME": name, 
                                           "OPENED": "Y",
                                           "SOURCE_ID": "WEBFORM",
                                           "COMMENTS": "с сайта",
                                           "PHONE": [{"VALUE": phone}]})
        result = bx.callMethod('crm.deal.add',
                       fields={
                           "TITLE": f"{name} ({phone})", 
                           "TYPE_ID": "GOODS", 
                           "STAGE_ID": "NEW", 
                           "CONTACT_ID": contact_id, 
                           "SOURCE_ID": "WEBFORM",
                           "SOURCE_DESCRIPTION": "с сайта",
                           "OPENED": "Y",
                           "ADDITIONAL_INFO": description
                           })
        crm_error = f"success {result}"
    except Exception as e:
        crm_status = False
        crm_error = str(e) + str(result)
    finally:
        instanse.crm_status = crm_status
        instanse.crm_error = crm_error
        instanse.save()
    return crm_status


def feedback_save(request):
    if request.method == "POST":
        form = FeedbackForm(data=request.POST)
        if form.is_valid():
            ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
            form.save(commit=False)
            inst = form.instance
            inst.ip_address = ip
            form.save()
            # status = create_on_crm(inst, inst.name, inst.phone)
            messages.success(request, 'Ваш контакт успешно отправлен, менеджер свяжется с вами')
        else:
            print(form.errors)
    return HttpResponseRedirect('/')

def feedback_ajax(request):
    if request.method == "POST":
        print(request.POST)
        form = FeedbackForm(data=request.POST)
        if form.is_valid():
            ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
            form.save(commit=False)
            inst = form.instance
            inst.ip_address = ip
            form.save()
            data = {"status": True}
        else:
            data = {"status": False, "errors": form.errors}
        return JsonResponse(data)
    else:
        return JsonResponse({"status": False, "errors": ['not ajax']})


def construction_modal(request):
    """Отображение страницы с модальным окном"""
    
    # Данные для формы
    context = {
        'building_types': [
            ('house', 'Жилой дом'),
            ('extension', 'Пристройка/Пристрой'),
            ('garage', 'Гараж'),
            ('banya', 'Баня/Сауна'),
            ('office', 'Офисное здание'),
            ('warehouse', 'Производственное помещение/Склад'),
            ('greenhouse', 'Теплица/Оранжерея'),
            ('other', 'Другое'),
        ],
        
        'floor_options': [
            ('1', 'Одноэтажный'),
            ('1.5', 'Полутораэтажный'),
            ('2', 'Двухэтажный'),
            ('2+', 'Более двух этажей'),
            ('mansard', 'С мансардой'),
            ('undecided', 'Еще думаю/Нужна консультация'),
        ],
        
        'features': [
            ('basement', 'Цокольный этаж/подвал'),
            ('terrace', 'Терраса/веранда'),
            ('balcony', 'Балкон'),
            ('garage_included', 'Встроенный гараж'),
            ('pool', 'Бассейн'),
            ('sauna', 'Сауна/хамам'),
        ],
        
        'project_options': [
            ('has_project', 'Имеется готовый проект'),
            ('has_sketch', 'Есть только эскиз/наброски'),
            ('need_consultation', 'Нужна консультация для разработки проекта'),
        ],
    }
    
    return render(request, 'modal_form.html', context)

def submit_construction_request(request):
    """Обработка отправки формы"""
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            building_type = request.POST.get('building_type')
            floor_count = request.POST.get('floor_count')
            project_status = request.POST.get('project_status')
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            contact_methods = request.POST.getlist('contact_method')
            comments = request.POST.get('comments', '')
            
            # Получаем выбранные особенности
            features = request.POST.getlist('features', [])
            
            # Создаем объект заявки
            request_data = {
                'building_type': dict(dict(request.POST.lists()).get('building_types', [])).get(building_type, building_type),
                'floor_count': floor_count,
                'project_status': project_status,
                'name': name,
                'phone': phone,
                'email': email,
                'contact_methods': contact_methods,
                'features': features,
                'comments': comments,
                'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ip_address': request.META.get('REMOTE_ADDR'),
            }
            
            # Сохраняем в файл или БД (здесь пример с JSON файлом)
            import os
            from django.conf import settings
            
            data_dir = os.path.join(settings.BASE_DIR, 'construction_requests')
            os.makedirs(data_dir, exist_ok=True)
            
            filename = f"request_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name.replace(' ', '_')}.json"
            filepath = os.path.join(data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=2)
            
            # Отправляем email уведомление
            if settings.EMAIL_HOST_USER:
                send_notification_email(request_data)
            
            # Возвращаем успешный ответ
            return JsonResponse({
                'success': True,
                'message': 'Заявка успешно отправлена!',
                'data': request_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка при отправке заявки: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Некорректный метод запроса'
    }, status=405)

def send_notification_email(request_data):
    """Отправка email уведомления"""
    
    # Email администратору
    admin_subject = f"Новая заявка на консультацию по строительству от {request_data['name']}"
    admin_message = render_to_string('emails/admin_notification.txt', request_data)
    
    send_mail(
        admin_subject,
        admin_message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )
    
    # Email клиенту
    client_subject = "Спасибо за вашу заявку на консультацию по строительству"
    client_message = render_to_string('emails/client_confirmation.txt', request_data)
    
    send_mail(
        client_subject,
        client_message,
        settings.DEFAULT_FROM_EMAIL,
        [request_data['email']],
        fail_silently=False,
    )

class QuestionViews(TemplateView):
    template_name = 'feedback/question.html'

def _send_to_crm(calculation_request):
    # Отправка email администратору
    admin_subject = f"Новая заявка на расчёт от {calculation_request.name}"
    admin_message = f"""
    Новая заявка на расчёт дома ThermoBlock

    Контактная информация:
    Имя: {calculation_request.name} {calculation_request.surname}
    Телефон: {calculation_request.phone}
    Email: {calculation_request.email or 'не указан'}
    Способ связи: {calculation_request.get_contact_method_display()}

    Детали проекта:
    Тип дома: {calculation_request.get_house_type_display()}
    Участок: {calculation_request.get_land_status_display()}
    Проект: {calculation_request.get_project_status_display()}
    Сроки: {calculation_request.get_timeline_display()}
    Оплата: {calculation_request.get_payment_method_display()}

    Комментарии: {calculation_request.comments or 'нет'}

    Согласие на обработку данных: {'Да' if calculation_request.data_agreement else 'Нет'}
    """
    try:
        send_mail(
            admin_subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(e)
        return False

def _send_to_client(calculation_request):
    client_subject = "Ваша заявка принята - ThermoBlock"
    client_message = f"""
    Здравствуйте, {calculation_request.name}!

    Спасибо за вашу заявку на расчёт стоимости дома.
    Мы получили ваши ответы и уже работаем над подготовкой коммерческого предложения.

    Наш специалист свяжется с вами в течение 24 часов по выбранному способу связи: 
    {calculation_request.get_contact_method_display()}.

    С уважением,
    Команда ThermoBlock
    Телефон: +7 (3012) 20-63-20
    Сайт: https://thermoblock.ru
    """
    
    try:
        send_mail(
            client_subject,
            client_message,
            settings.DEFAULT_FROM_EMAIL,
            [calculation_request.email],
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(e)
        return False



@csrf_exempt
@require_POST
def submit_request(request):
    try:
        data = json.loads(request.body)
        form = CalculationRequestForm(data)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Неверный формат данных'
        }, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({
            'success': False,
            'message': f'Ошибка сервера: {str(e)}'
        }, status=500) 
    
    if form.is_valid():
        calculation_request = form.save()
        if _send_to_crm(calculation_request):
            print('отправил на CRM')
        else:
            print('ошибка отправки в црм')
        # Отправка email клиенту (если указан email)
        if calculation_request.email:
            if _send_to_client(calculation_request):
                print('успешно на почту отправили клиенту')
            else:
                print('подозрительный почтовый ящик - сообщение не отправлено')
        
        return JsonResponse({
            'success': True,
            'message': 'Заявка успешно отправлена!'
        })
    else:
        # Собираем ошибки формы
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list[0]
        print(errors)
        return JsonResponse({
            'success': False,
            'message': 'Пожалуйста, исправьте ошибки в форме',
            'errors': errors
        }, status=400)
            
    