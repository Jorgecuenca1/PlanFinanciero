"""Template tags para el modulo de evaluacion"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario por clave"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def porcentaje(valor, total):
    """Calcula el porcentaje de un valor sobre un total"""
    if total == 0:
        return 0
    return round((valor / total) * 100, 1)


@register.filter
def estado_class(estado):
    """Retorna la clase CSS para un estado de evaluacion"""
    clases = {
        'C': 'bg-success',
        'NC': 'bg-danger',
        'NA': 'bg-secondary',
        'PE': 'bg-warning text-dark',
    }
    return clases.get(estado, 'bg-secondary')


@register.filter
def estado_documento_class(estado):
    """Retorna la clase CSS para un estado de documento"""
    clases = {
        'NT': 'bg-secondary',
        'ED': 'bg-info',
        'AP': 'bg-success',
    }
    return clases.get(estado, 'bg-secondary')
