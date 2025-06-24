# productos/templatetags/extra_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, key):
    return value.split(key)

@register.filter
def trim(value):
    return value.strip()