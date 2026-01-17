from dataclasses import fields
from django.forms import ModelForm
from captcha.fields import CaptchaField
from .models import Feedback

class FeedbackForm(ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = Feedback
        fields = ('name', 'phone')
