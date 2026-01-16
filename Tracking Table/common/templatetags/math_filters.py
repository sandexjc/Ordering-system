from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    # Multiply the value by the argument.
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def div(value, arg):
    # Divide the value by the argument.
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return ''

@register.filter
def at_least(value, minimum):
    try:
        return max(float(value), float(minimum))
    except (TypeError, ValueError):
        return value

@register.filter
def sub(value, arg):
    try:
        return float(value) - float(arg)
    except Exception:
        return ''

