from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import  HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings


class IndexView(TemplateView):
    """Главная страница"""
    template_name = 'about/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ThermoBlock | О нас'
        return context
    
class PrivacyView(TemplateView):
    """Соглашение о персональных данных"""
    template_name = 'about/userprivacy.html'

class AgreementView(TemplateView):
    """Пользовательское соглашение"""
    template_name = 'about/useragreement.html'

class ContactView(TemplateView):
    """Карточка предприятия"""
    template_name = 'about/contact.html'


def contacts_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Определяем тему письма
        subject_dict = {
            'general': 'Общий вопрос',
            'sales': 'Запрос по продукции',
            'project': 'Проектирование',
            'construction': 'Строительство под ключ',
            'cooperation': 'Сотрудничество'
        }
        subject_text = subject_dict.get(subject, 'Общий вопрос')
        
        # Формируем тело письма
        email_message = f"""
        Новая заявка с сайта thermoblock.ru
        
        Имя: {name}
        Телефон: {phone}
        Email: {email}
        Тема: {subject_text}
        
        Сообщение:
        {message}
        
        ---
        Это автоматическое письмо, не отвечайте на него.
        """
        
        try:
            # Отправляем email администратору
            send_mail(
                f'Новая заявка: {subject_text} от {name}',
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            
            # Отправляем подтверждение клиенту
            client_subject = 'Ваше сообщение получено'
            client_message = f"""
            Уважаемый(ая) {name},
            
            Спасибо за ваше сообщение! Мы получили вашу заявку и свяжемся с вами в ближайшее время.
            
            Ваше сообщение:
            {message}
            
            С уважением,
            Команда ThermoBlock
            """
            
            send_mail(
                client_subject,
                client_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.')
            return redirect('about:contact')
            
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при отправке: {str(e)}')
            return redirect('about:contacts')
    
    # Контекст для страницы
    context = {
        'page_title': 'Контакты',
        'meta_description': 'Контакты ООО "Строй Тех" - производителя термоблоков ThermoBlock. Телефоны, адреса, реквизиты.',
    }
    
    return render(request, 'about/contact.html', context)