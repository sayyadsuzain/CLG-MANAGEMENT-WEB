from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key."""
    return dictionary.get(key)

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def div(value, arg):
    """Divide the value by the arg."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def map(value, attr):
    """Map a list of dictionaries to a list of values for a specific key."""
    try:
        return [item.get(attr) if isinstance(item, dict) else getattr(item, attr) for item in value]
    except (AttributeError, KeyError, TypeError):
        return []

@register.filter
def sum(value):
    """Sum a list of numbers."""
    try:
        return sum(float(v) for v in value if v is not None)
    except (ValueError, TypeError):
        return 0

@register.filter
def filter(value, attr):
    """Filter a list of dictionaries based on whether they have a non-None value for a specific key."""
    try:
        return [item for item in value if (isinstance(item, dict) and item.get(attr) is not None) or (not isinstance(item, dict) and getattr(item, attr) is not None)]
    except (AttributeError, KeyError, TypeError):
        return [] 