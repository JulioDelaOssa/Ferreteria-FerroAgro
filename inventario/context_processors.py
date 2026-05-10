from django.db.models import F

from .models import Producto, Venta


def notificaciones_globales(request):
    if not request.user.is_authenticated:
        return {
            'alertas_total': 0,
            'alertas_stock_bajo': 0,
            'alertas_agotados': 0,
            'alertas_ventas_pendientes': 0,
        }

    stock_bajo = Producto.objects.filter(
        stock__gt=0,
        stock__lte=F('stock_minimo')
    ).count()

    agotados = Producto.objects.filter(
        stock=0
    ).count()

    ventas_pendientes = Venta.objects.filter(
        estado='pendiente'
    ).count()

    alertas_total = stock_bajo + agotados + ventas_pendientes

    return {
        'alertas_total': alertas_total,
        'alertas_stock_bajo': stock_bajo,
        'alertas_agotados': agotados,
        'alertas_ventas_pendientes': ventas_pendientes,
    }