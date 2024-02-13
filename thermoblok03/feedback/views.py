from math import e
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponseRedirect
from .forms import FeedbackForm
from django.contrib import messages

import bitrix24
# Create your views here.

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
            status = create_on_crm(inst, inst.name, inst.phone)
            messages.success(request, 'Ваш контакт успешно отправлен, менеджер свяжется с вами')
            if not status:
                print('неотправилось')
        else:
            print(form.errors)
    return HttpResponseRedirect('/')


