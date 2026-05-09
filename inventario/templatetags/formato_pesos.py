from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def pesos(valor):
    if valor is None:
        return '$0'

    try:
        numero = Decimal(valor)
    except (InvalidOperation, TypeError, ValueError):
        return '$0'

    numero = int(numero)
    numero_formateado = f'{numero:,}'.replace(',', '.')

    return f'${numero_formateado}'