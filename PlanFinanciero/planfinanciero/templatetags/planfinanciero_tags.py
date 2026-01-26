from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario usando una clave variable"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def currency(value):
    """Formatea un valor como moneda colombiana"""
    try:
        return f"${value:,.0f}"
    except (ValueError, TypeError):
        return value


@register.filter
def percentage(value, total):
    """Calcula el porcentaje de un valor respecto al total"""
    try:
        if total == 0:
            return 0
        return (value / total) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
