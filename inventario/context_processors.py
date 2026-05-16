from django.db.models import F
from django.urls import reverse

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


def breadcrumbs_globales(request):
    if not request.user.is_authenticated or not getattr(request, 'resolver_match', None):
        return {'breadcrumb_items': []}

    url_name = request.resolver_match.url_name
    grupos = {
        'dashboard': [('Dashboard', 'dashboard')],
        'producto_lista': [('Productos', 'producto_lista')],
        'producto_crear': [('Productos', 'producto_lista'), ('Registrar', None)],
        'producto_editar': [('Productos', 'producto_lista'), ('Editar', None)],
        'inventario_lista': [('Inventario', 'inventario_lista')],
        'ajustar_stock': [('Inventario', 'inventario_lista'), ('Ajustar stock', None)],
        'ventas_panel': [('Ventas', 'ventas_panel')],
        'venta_nueva': [('Ventas', 'ventas_panel'), ('Nueva venta', None)],
        'venta_detalle': [('Ventas', 'ventas_panel'), ('Detalle', None)],
        'venta_editar': [('Ventas', 'ventas_panel'), ('Editar factura', None)],
        'categoria_lista': [('Categorías', 'categoria_lista')],
        'categoria_crear': [('Categorías', 'categoria_lista'), ('Registrar', None)],
        'categoria_editar': [('Categorías', 'categoria_lista'), ('Editar', None)],
        'proveedor_lista': [('Proveedores', 'proveedor_lista')],
        'proveedor_crear': [('Proveedores', 'proveedor_lista'), ('Registrar', None)],
        'proveedor_editar': [('Proveedores', 'proveedor_lista'), ('Editar', None)],
        'cliente_lista': [('Clientes', 'cliente_lista')],
        'cliente_crear': [('Clientes', 'cliente_lista'), ('Registrar', None)],
        'cliente_editar': [('Clientes', 'cliente_lista'), ('Editar', None)],
        'vendedor_lista': [('Vendedores', 'vendedor_lista')],
        'vendedor_crear': [('Vendedores', 'vendedor_lista'), ('Registrar', None)],
        'vendedor_editar': [('Vendedores', 'vendedor_lista'), ('Editar', None)],
    }

    if url_name not in grupos:
        return {'breadcrumb_items': []}

    inicio_url = 'dashboard' if request.user.is_staff or request.user.is_superuser else 'ventas_panel'
    items = [{'label': 'Inicio', 'url': reverse(inicio_url), 'active': False}]

    for index, item in enumerate(grupos[url_name]):
        label, route = item
        is_last = index == len(grupos[url_name]) - 1
        url = reverse(route) if route and not is_last else ''
        items.append({'label': label, 'url': url, 'active': is_last})

    return {'breadcrumb_items': items}
