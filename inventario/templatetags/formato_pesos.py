from django import template

register = template.Library()

@register.filter
def pesos_colombianos(valor):
    if valor is None:
        return '$ 0'

    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return '$ 0'

    if valor.is_integer():
        valor_formateado = f'{int(valor):,}'.replace(',', '.')
        return f'$ {valor_formateado}'

    valor_formateado = f'{valor:,.2f}'
    valor_formateado = valor_formateado.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'$ {valor_formateado}'