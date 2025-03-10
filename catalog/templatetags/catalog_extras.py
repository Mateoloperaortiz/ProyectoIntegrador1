from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
        
@register.filter
def subtract(value, arg):
    """Subtracts the argument from the value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0