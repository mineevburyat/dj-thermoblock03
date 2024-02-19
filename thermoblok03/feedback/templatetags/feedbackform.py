from urllib import request
from django import template
from ..forms import FeedbackForm

register = template.Library()

@register.simple_tag()
def get_form(request):
   return FeedbackForm(data=request.POST)