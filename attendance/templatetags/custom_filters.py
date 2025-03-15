from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.simple_tag
def get_current_time():
    return timezone.now() 