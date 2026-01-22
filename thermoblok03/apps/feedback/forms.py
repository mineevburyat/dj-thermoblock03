from dataclasses import fields
from django.forms import ModelForm
from captcha.fields import CaptchaField
from .models import Feedback
from django import forms
from .models import CalculationRequest

class FeedbackForm(ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = Feedback
        fields = ('name', 'phone')


class CalculationRequestForm(forms.ModelForm):
    class Meta:
        model = CalculationRequest
        fields = '__all__'
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Простая валидация телефона
        if len(phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
            raise forms.ValidationError('Введите корректный номер телефона')
        return phone
    
    def clean_data_agreement(self):
        data_agreement = self.cleaned_data.get('data_agreement')
        if not data_agreement:
            raise forms.ValidationError('Необходимо согласие на обработку персональных данных')
        return data_agreement