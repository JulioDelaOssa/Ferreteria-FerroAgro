from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Count, F, Sum
from django.utils import timezone

from .models import Categoria, DetalleVenta, Movimientos, Producto, Venta


def rango_dia(fecha):
    inicio = timezone.make_aware(
        datetime.combine(fecha, datetime.min.time())
    )

    fin = timezone.make_aware(
        datetime.combine(fecha, datetime.max.time())
    )

    return inicio, fin


def rango_mes(year, month):
    inicio_mes = timezone.make_aware(
        datetime(year, month, 1, 0, 0, 0)
    )

    if month == 12:
        inicio_siguiente_mes = timezone.make_aware(
            datetime(year + 1, 1, 1, 0, 0, 0)
        )
    else:
        inicio_siguiente_mes = timezone.make_aware(
            datetime(year, month + 1, 1, 0, 0, 0)
        )

    return inicio_mes, inicio_siguiente_mes


def obtener_datos_dashboard():
    hoy = timezone.localdate()
    ayer = hoy - timedelta(days=1)
    inicio_semana = hoy - timedelta(days=6)
    inicio_mes_fecha = hoy.replace(day=1)

    inicio_hoy, fin_hoy = rango_dia(hoy)
    inicio_ayer, fin_ayer = rango_dia(ayer)

    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(activo=True).count()

    productos_nuevos_mes = Producto.objects.filter(
        fecha_registro__date__gte=inicio_mes_fecha
    ).count()

    stock_bajo = Producto.objects.filter(
        stock__gt=0,
        stock__lte=F('stock_minimo')
    ).count()

    agotados = Producto.objects.filter(stock=0).count()

    en_stock = Producto.objects.filter(
        stock__gt=F('stock_minimo')
    ).count()

    sin_movimiento = Producto.objects.annotate(
        total_movimientos=Count('movimientos')
    ).filter(total_movimientos=0).count()

    ventas_hoy_qs = Venta.objects.filter(
        fecha__gte=inicio_hoy,
        fecha__lte=fin_hoy,
        estado='pagada'
    )

    ventas_dia = ventas_hoy_qs.count()

    ingresos_hoy = ventas_hoy_qs.aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')

    ventas_ayer = Venta.objects.filter(
        fecha__gte=inicio_ayer,
        fecha__lte=fin_ayer,
        estado='pagada'
    ).count()

    if ventas_ayer > 0:
        porcentaje_ventas = ((ventas_dia - ventas_ayer) / ventas_ayer) * 100
        porcentaje_ventas_dia = f'{porcentaje_ventas:+.0f}% vs ayer'
    else:
        porcentaje_ventas_dia = 'Sin datos suficientes'

    inicio_mes, inicio_siguiente_mes = rango_mes(hoy.year, hoy.month)

    ventas_mes_qs = Venta.objects.filter(
        fecha__gte=inicio_mes,
        fecha__lt=inicio_siguiente_mes,
        estado='pagada'
    )

    ingresos_mes = ventas_mes_qs.aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')

    if hoy.month == 1:
        mes_anterior = 12
        year_anterior = hoy.year - 1
    else:
        mes_anterior = hoy.month - 1
        year_anterior = hoy.year

    inicio_mes_anterior, inicio_mes_actual = rango_mes(year_anterior, mes_anterior)

    ingresos_mes_anterior = Venta.objects.filter(
        fecha__gte=inicio_mes_anterior,
        fecha__lt=inicio_mes_actual,
        estado='pagada'
    ).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')

    if ingresos_mes_anterior > 0:
        porcentaje_ingresos = ((ingresos_mes - ingresos_mes_anterior) / ingresos_mes_anterior) * 100
        porcentaje_ingresos_mes = f'{porcentaje_ingresos:+.0f}% vs mes anterior'
    else:
        porcentaje_ingresos_mes = 'Sin datos suficientes'

    ventas_semana = []
    ingresos_por_dia = []

    for i in range(7):
        dia = inicio_semana + timedelta(days=i)

        inicio_dia, fin_dia = rango_dia(dia)

        ventas_dia_qs = Venta.objects.filter(
            fecha__gte=inicio_dia,
            fecha__lte=fin_dia,
            estado='pagada'
        )

        total_dia = ventas_dia_qs.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')

        cantidad_dia = ventas_dia_qs.count()

        ingresos_por_dia.append(total_dia)

        ventas_semana.append({
            'dia': dia.strftime('%d/%m'),
            'total': total_dia,
            'cantidad': cantidad_dia,
            'altura_ventas': 0,
        })

    max_ingresos = max(ingresos_por_dia) if ingresos_por_dia else Decimal('0')
    hay_ventas_semana = max_ingresos > 0

    for item in ventas_semana:
        if max_ingresos > 0:
            item['altura_ventas'] = max(
                12,
                int((item['total'] / max_ingresos) * 100)
            )
        else:
            item['altura_ventas'] = 0

    if total_productos > 0:
        porcentaje_en_stock_num = round((en_stock / total_productos) * 100)
        porcentaje_stock_bajo_num = round((stock_bajo / total_productos) * 100)
        porcentaje_agotado_num = round((agotados / total_productos) * 100)
        porcentaje_sin_movimiento_num = round((sin_movimiento / total_productos) * 100)
        hay_inventario = True
    else:
        porcentaje_en_stock_num = 0
        porcentaje_stock_bajo_num = 0
        porcentaje_agotado_num = 0
        porcentaje_sin_movimiento_num = 0
        hay_inventario = False

    porcentaje_en_stock = f'{porcentaje_en_stock_num}%'
    porcentaje_stock_bajo = f'{porcentaje_stock_bajo_num}%'
    porcentaje_agotado = f'{porcentaje_agotado_num}%'
    porcentaje_sin_movimiento = f'{porcentaje_sin_movimiento_num}%'

    donut_en_stock_fin = porcentaje_en_stock_num
    donut_stock_bajo_fin = porcentaje_en_stock_num + porcentaje_stock_bajo_num
    donut_agotado_fin = donut_stock_bajo_fin + porcentaje_agotado_num
    donut_sin_movimiento_fin = donut_agotado_fin + porcentaje_sin_movimiento_num

    ventas_recientes = Venta.objects.select_related(
        'vendedor'
    ).prefetch_related(
        'detalles'
    ).order_by('-fecha')[:5]

    productos_stock_bajo = Producto.objects.filter(
        stock__gt=0,
        stock__lte=F('stock_minimo')
    ).select_related(
        'categoria',
        'proveedor'
    ).order_by('stock')[:5]

    movimientos_recientes = Movimientos.objects.select_related(
        'producto',
        'usuario'
    ).order_by('-fecha')[:5]

    detalles_vendidos = DetalleVenta.objects.select_related(
        'producto'
    ).filter(
        producto__isnull=False,
        venta__estado='pagada'
    )

    acumulado_productos = defaultdict(lambda: {
        'producto': None,
        'unidades': 0,
        'total': Decimal('0')
    })

    for detalle in detalles_vendidos:
        item = acumulado_productos[detalle.producto_id]
        item['producto'] = detalle.producto
        item['unidades'] += detalle.cantidad
        item['total'] += detalle.subtotal

    productos_mas_vendidos = sorted(
        acumulado_productos.values(),
        key=lambda item: item['unidades'],
        reverse=True
    )[:5]

    valor_inventario = Decimal('0')

    for producto in Producto.objects.all():
        valor_inventario += producto.precio * producto.stock

    total_unidades_vendidas = DetalleVenta.objects.filter(
        venta__estado='pagada'
    ).aggregate(
        total=Sum('cantidad')
    )['total'] or 0

    if productos_activos > 0:
        rotacion_promedio = round(total_unidades_vendidas / productos_activos, 1)
    else:
        rotacion_promedio = 0

    ultimo_movimiento = Movimientos.objects.order_by('-fecha').first()

    if ultimo_movimiento:
        ultima_actualizacion = timezone.localtime(
            ultimo_movimiento.fecha
        ).strftime('%d/%m/%Y %I:%M %p')
    else:
        ultima_actualizacion = 'Sin datos'

    categorias = Categoria.objects.annotate(
        total_categoria=Count('productos')
    ).filter(
        total_categoria__gt=0
    ).order_by('-total_categoria')[:5]

    distribucion_categorias = []

    for categoria in categorias:
        if total_productos > 0:
            porcentaje = round((categoria.total_categoria / total_productos) * 100)
        else:
            porcentaje = 0

        distribucion_categorias.append({
            'nombre': categoria.nombre,
            'total': categoria.total_categoria,
            'porcentaje': porcentaje
        })

    ventas_pendientes = Venta.objects.filter(
        estado='pendiente'
    ).count()

    alertas_total = stock_bajo + agotados + ventas_pendientes

    return {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'productos_nuevos_mes': productos_nuevos_mes,
        'stock_bajo': stock_bajo,
        'agotados': agotados,
        'ventas_dia': ventas_dia,
        'ingresos_hoy': ingresos_hoy,
        'ingresos_mes': ingresos_mes,
        'porcentaje_ventas_dia': porcentaje_ventas_dia,
        'porcentaje_ingresos_mes': porcentaje_ingresos_mes,
        'ventas_semana': ventas_semana,
        'hay_ventas_semana': hay_ventas_semana,
        'hay_inventario': hay_inventario,
        'porcentaje_en_stock': porcentaje_en_stock,
        'porcentaje_stock_bajo': porcentaje_stock_bajo,
        'porcentaje_agotado': porcentaje_agotado,
        'porcentaje_sin_movimiento': porcentaje_sin_movimiento,
        'porcentaje_en_stock_num': porcentaje_en_stock_num,
        'porcentaje_stock_bajo_num': porcentaje_stock_bajo_num,
        'porcentaje_agotado_num': porcentaje_agotado_num,
        'porcentaje_sin_movimiento_num': porcentaje_sin_movimiento_num,
        'donut_en_stock_fin': donut_en_stock_fin,
        'donut_stock_bajo_fin': donut_stock_bajo_fin,
        'donut_agotado_fin': donut_agotado_fin,
        'donut_sin_movimiento_fin': donut_sin_movimiento_fin,
        'ventas_recientes': ventas_recientes,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_mas_vendidos': productos_mas_vendidos,
        'movimientos_recientes': movimientos_recientes,
        'valor_inventario': valor_inventario,
        'productos_sin_movimiento': sin_movimiento,
        'rotacion_promedio': rotacion_promedio,
        'ultima_actualizacion': ultima_actualizacion,
        'distribucion_categorias': distribucion_categorias,
        'alertas_total': alertas_total,
    }