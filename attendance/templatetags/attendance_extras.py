from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a value from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None or not hasattr(dictionary, 'get'):
        return None
    return dictionary.get(key)

@register.filter
def class_name(obj):
    """
    Template filter to get the class name of an object.
    Usage: {{ object|class_name }}
    """
    return obj.__class__.__name__

@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return value 