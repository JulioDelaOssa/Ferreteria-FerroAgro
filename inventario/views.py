from decimal import Decimal, InvalidOperation
from datetime import datetime, time

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .forms import (
    AjusteStockForm,
    CategoriaForm,
    ProductoForm,
    ProveedorForm,
    VendedorForm,
)
from .funciones_dashboard import obtener_datos_dashboard
from .models import Categoria, DetalleVenta, Movimientos, Producto, Proveedor, Venta


def es_administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


admin_required = user_passes_test(es_administrador, login_url='ventas_panel')


def formato_pesos_pdf(valor):
    if valor is None:
        return '$0'

    try:
        numero = Decimal(valor)
    except (InvalidOperation, TypeError, ValueError):
        return '$0'

    numero = int(numero)
    return f'${numero:,}'.replace(',', '.')


def crear_documento_pdf(response, titulo, subtitulo):
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm
    )

    styles = getSampleStyleSheet()
    elements = [
        Paragraph('FerroAgro Ayapel', styles['Title']),
        Paragraph(titulo, styles['Heading2']),
        Paragraph(subtitulo, styles['Normal']),
        Spacer(1, 14),
    ]

    return doc, styles, elements


def aplicar_estilo_tabla(tabla):
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#14532d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))

    return tabla


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse('post_login')


def landing(request):
    if request.user.is_authenticated:
        return redirect('post_login')

    productos_destacados = Producto.objects.filter(
        activo=True
    ).order_by('-fecha_registro')[:8]

    return render(request, 'landing.html', {
        'productos_destacados': productos_destacados
    })


@login_required
def post_login(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')

    return redirect('ventas_panel')


@login_required
@admin_required
def dashboard(request):
    context = obtener_datos_dashboard()
    return render(request, 'inventario/dashboard.html', context)


@login_required
@admin_required
def producto_lista(request):
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')

    productos = Producto.objects.select_related(
        'categoria',
        'proveedor'
    ).all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(proveedor__nombre__icontains=query)
        )

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if estado == 'activo':
        productos = productos.filter(activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(activo=False)
    elif estado == 'stock_bajo':
        productos = productos.filter(stock__gt=0, stock__lte=F('stock_minimo'))
    elif estado == 'agotado':
        productos = productos.filter(stock=0)

    categorias = Categoria.objects.filter(activo=True)

    return render(request, 'inventario/producto_lista.html', {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id,
        'estado': estado,
    })


@login_required
@admin_required
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)

        if form.is_valid():
            producto = form.save()

            if producto.stock > 0:
                Movimientos.objects.create(
                    producto=producto,
                    tipo='entrada',
                    cantidad=producto.stock,
                    motivo='Registro inicial del producto',
                    usuario=request.user
                )

            messages.success(request, 'Producto creado correctamente.')
            return redirect('producto_lista')
    else:
        form = ProductoForm()

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'titulo': 'Agregar producto',
        'volver_url': reverse('producto_lista')
    })


@login_required
@admin_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)

        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'producto': producto,
        'titulo': 'Editar producto',
        'volver_url': reverse('producto_lista')
    })


@login_required
@admin_required
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('producto_lista')

    return render(request, 'inventario/producto_confirmar_eliminar.html', {
        'producto': producto
    })


@login_required
@admin_required
def categoria_lista(request):
    categorias = Categoria.objects.annotate(
        total_productos=Count('productos')
    ).order_by('nombre')

    return render(request, 'inventario/categoria_lista.html', {
        'categorias': categorias
    })


@login_required
@admin_required
def categoria_crear(request):
    es_popup = request.GET.get('popup') == '1'

    if request.method == 'POST':
        form = CategoriaForm(request.POST)

        if form.is_valid():
            categoria = form.save()

            if es_popup:
                return render(request, 'inventario/cerrar_popup.html', {
                    'tipo': 'categoria',
                    'objeto': categoria
                })

            messages.success(request, 'Categoría creada correctamente.')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()

    return render(request, 'inventario/categoria_form.html', {
        'form': form,
        'titulo': 'Agregar categoría',
        'volver_url': reverse('categoria_lista'),
        'icono': 'ri-price-tag-3-line',
        'popup': es_popup,
        'base_template': 'popup_base.html' if es_popup else 'base.html'
    })


@login_required
@admin_required
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'inventario/categoria_form.html', {
        'form': form,
        'categoria': categoria,
        'titulo': 'Editar categoría',
        'volver_url': reverse('categoria_lista'),
        'icono': 'ri-price-tag-3-line',
        'popup': False,
        'base_template': 'base.html'
    })


@login_required
@admin_required
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
        return redirect('categoria_lista')

    return render(request, 'inventario/categoria_confirmar_eliminar.html', {
        'categoria': categoria
    })


@login_required
@admin_required
def proveedor_lista(request):
    proveedores = Proveedor.objects.annotate(
        total_productos=Count('productos')
    ).order_by('nombre')

    return render(request, 'inventario/proveedor_lista.html', {
        'proveedores': proveedores
    })


@login_required
@admin_required
def proveedor_crear(request):
    es_popup = request.GET.get('popup') == '1'

    if request.method == 'POST':
        form = ProveedorForm(request.POST)

        if form.is_valid():
            proveedor = form.save()

            if es_popup:
                return render(request, 'inventario/cerrar_popup.html', {
                    'tipo': 'proveedor',
                    'objeto': proveedor
                })

            messages.success(request, 'Proveedor creado correctamente.')
            return redirect('proveedor_lista')
    else:
        form = ProveedorForm()

    return render(request, 'inventario/proveedor_form.html', {
        'form': form,
        'titulo': 'Agregar proveedor',
        'volver_url': reverse('proveedor_lista'),
        'icono': 'ri-truck-line',
        'popup': es_popup,
        'base_template': 'popup_base.html' if es_popup else 'base.html'
    })


@login_required
@admin_required
def proveedor_editar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)

        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado correctamente.')
            return redirect('proveedor_lista')
    else:
        form = ProveedorForm(instance=proveedor)

    return render(request, 'inventario/proveedor_form.html', {
        'form': form,
        'proveedor': proveedor,
        'titulo': 'Editar proveedor',
        'volver_url': reverse('proveedor_lista'),
        'icono': 'ri-truck-line',
        'popup': False,
        'base_template': 'base.html'
    })


@login_required
@admin_required
def proveedor_eliminar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado correctamente.')
        return redirect('proveedor_lista')

    return render(request, 'inventario/proveedor_confirmar_eliminar.html', {
        'proveedor': proveedor
    })


@login_required
@admin_required
def inventario_lista(request):
    tipo_movimiento = request.GET.get('tipo', '').strip()
    fecha_desde = request.GET.get('desde', '').strip()
    fecha_hasta = request.GET.get('hasta', '').strip()
    fecha_desde_obj = parse_date(fecha_desde) if fecha_desde else None
    fecha_hasta_obj = parse_date(fecha_hasta) if fecha_hasta else None

    productos = Producto.objects.select_related(
        'categoria',
        'proveedor'
    ).order_by('nombre')

    total_productos = productos.count()

    stock_bajo = Producto.objects.filter(
        stock__gt=0,
        stock__lte=F('stock_minimo')
    ).count()

    agotados = Producto.objects.filter(stock=0).count()

    movimientos = Movimientos.objects.select_related(
        'producto',
        'usuario'
    ).order_by('-fecha')

    if tipo_movimiento:
        movimientos = movimientos.filter(tipo=tipo_movimiento)

    if fecha_desde_obj:
        inicio_desde = timezone.make_aware(
            datetime.combine(fecha_desde_obj, time.min)
        )
        movimientos = movimientos.filter(fecha__gte=inicio_desde)

    if fecha_hasta_obj:
        fin_hasta = timezone.make_aware(
            datetime.combine(fecha_hasta_obj, time.max)
        )
        movimientos = movimientos.filter(fecha__lte=fin_hasta)

    movimientos = movimientos[:120]

    return render(request, 'inventario/inventario_lista.html', {
        'productos': productos,
        'total_productos': total_productos,
        'stock_bajo': stock_bajo,
        'agotados': agotados,
        'movimientos': movimientos,
        'tipo_movimiento': tipo_movimiento,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'tipos_movimiento': Movimientos.TIPO_CHOICES,
    })


@login_required
@admin_required
def ajustar_stock(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = AjusteStockForm(request.POST)

        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']
            motivo = form.cleaned_data.get('motivo', '')

            if tipo == 'entrada':
                producto.stock += cantidad
                cantidad_movimiento = cantidad
            elif tipo == 'salida':
                if cantidad > producto.stock:
                    messages.error(
                        request,
                        'No puedes retirar más unidades de las disponibles.'
                    )
                    return redirect('ajustar_stock', pk=producto.pk)

                producto.stock -= cantidad
                cantidad_movimiento = -cantidad
            else:
                diferencia = cantidad - producto.stock
                producto.stock = cantidad
                cantidad_movimiento = diferencia

            producto.save()

            Movimientos.objects.create(
                producto=producto,
                tipo=tipo,
                cantidad=cantidad_movimiento,
                motivo=motivo,
                usuario=request.user
            )

            messages.success(request, 'Stock actualizado correctamente.')
            return redirect('inventario_lista')
    else:
        form = AjusteStockForm()

    return render(request, 'inventario/ajustar_stock.html', {
        'form': form,
        'producto': producto,
        'titulo': 'Ajustar stock',
        'volver_url': reverse('inventario_lista')
    })


@login_required
def ventas_panel(request):
    query = request.GET.get('q', '').strip()

    ventas = Venta.objects.select_related(
        'vendedor'
    ).prefetch_related(
        'detalles'
    ).order_by('-fecha')

    # Si el usuario es vendedor, solo puede ver sus propias ventas
    if not request.user.is_staff and not request.user.is_superuser:
        ventas = ventas.filter(vendedor=request.user)

    productos_disponibles = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).select_related(
        'categoria',
        'proveedor'
    ).order_by('nombre')

    if query:
        ventas = ventas.filter(
            Q(cliente_nombre__icontains=query) |
            Q(cliente_documento__icontains=query) |
            Q(metodo_pago__icontains=query)
        )

        productos_disponibles = productos_disponibles.filter(
            Q(nombre__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(proveedor__nombre__icontains=query)
        )

    total_ventas = ventas.count()

    ingresos = ventas.filter(
        estado='pagada'
    ).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')

    pendientes = ventas.filter(
        estado='pendiente'
    ).count()

    anuladas = ventas.filter(
        estado='anulada'
    ).count()

    return render(request, 'inventario/ventas_panel.html', {
        'ventas': ventas,
        'productos_disponibles': productos_disponibles,
        'total_ventas': total_ventas,
        'ingresos': ingresos,
        'pendientes': pendientes,
        'anuladas': anuladas,
        'query': query,
    })

@login_required
@transaction.atomic
def venta_nueva(request):
    productos = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).select_related(
        'categoria',
        'proveedor'
    ).order_by('nombre')

    vendedores = User.objects.filter(
        is_active=True,
        is_staff=False,
        is_superuser=False
    ).order_by('first_name', 'username')

    if request.method == 'POST':
        productos_ids = request.POST.getlist('producto_id')
        cantidades = request.POST.getlist('cantidad')

        vendedor_id = request.POST.get('vendedor_id')
        cliente_nombre = request.POST.get('cliente_nombre', '').strip()
        cliente_documento = request.POST.get('cliente_documento', '').strip()
        cliente_telefono = request.POST.get('cliente_telefono', '').strip()
        metodo_pago = request.POST.get('metodo_pago', 'efectivo')
        observaciones = request.POST.get('observaciones', '').strip()

        try:
            descuento = Decimal(request.POST.get('descuento') or '0')
        except (InvalidOperation, TypeError, ValueError):
            descuento = Decimal('0')

        if request.user.is_staff or request.user.is_superuser:
            if vendedor_id:
                vendedor = get_object_or_404(User, pk=vendedor_id, is_active=True)
            else:
                vendedor = request.user
        else:
            vendedor = request.user

        items = []

        for producto_id, cantidad in zip(productos_ids, cantidades):
            if not producto_id or not cantidad:
                continue

            producto = get_object_or_404(Producto, pk=producto_id, activo=True)

            try:
                cantidad = int(cantidad)
            except ValueError:
                cantidad = 0

            if cantidad <= 0:
                continue

            if cantidad > producto.stock:
                messages.error(
                    request,
                    f'No hay suficiente stock para {producto.nombre}.'
                )
                return redirect('venta_nueva')

            subtotal = producto.precio * cantidad

            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': producto.precio,
                'subtotal': subtotal
            })

        if not items:
            messages.error(request, 'Debes agregar al menos un producto a la venta.')
            return redirect('venta_nueva')

        subtotal_general = sum(item['subtotal'] for item in items)

        if descuento < 0:
            descuento = Decimal('0')

        if descuento > subtotal_general:
            descuento = subtotal_general

        total = subtotal_general - descuento

        venta = Venta.objects.create(
            vendedor=vendedor,
            cliente_nombre=cliente_nombre or 'Consumidor final',
            cliente_documento=cliente_documento,
            cliente_telefono=cliente_telefono,
            metodo_pago=metodo_pago,
            estado='pagada',
            subtotal=subtotal_general,
            descuento=descuento,
            total=total,
            observaciones=observaciones
        )

        for item in items:
            producto = item['producto']

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                producto_nombre=producto.nombre,
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario'],
                subtotal=item['subtotal']
            )

            producto.stock -= item['cantidad']
            producto.save()

            Movimientos.objects.create(
                producto=producto,
                tipo='salida',
                cantidad=-item['cantidad'],
                motivo=f'Venta factura #{venta.id}',
                usuario=request.user
            )

        messages.success(request, 'Venta registrada correctamente.')
        return redirect('venta_detalle', pk=venta.pk)

    return render(request, 'inventario/venta_nueva.html', {
        'productos': productos,
        'vendedores': vendedores
    })


@login_required
def venta_detalle(request, pk):
    venta = get_object_or_404(
        Venta.objects.select_related('vendedor').prefetch_related('detalles'),
        pk=pk
    )

    return render(request, 'inventario/venta_detalle.html', {
        'venta': venta
    })


@login_required
def factura_pdf(request, pk):
    venta = get_object_or_404(
        Venta.objects.select_related('vendedor').prefetch_related('detalles'),
        pk=pk
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura-{venta.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph('FerroAgro Ayapel', styles['Title']))
    elements.append(Paragraph('Factura de venta', styles['Heading2']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f'Factura: FAC-{venta.id}', styles['Normal']))
    elements.append(Paragraph(
        f'Fecha: {venta.fecha.strftime("%d/%m/%Y %I:%M %p")}',
        styles['Normal']
    ))
    elements.append(Paragraph(
        f'Cliente: {venta.cliente_nombre or "Consumidor final"}',
        styles['Normal']
    ))
    elements.append(Paragraph(
        f'Documento: {venta.cliente_documento or "No registrado"}',
        styles['Normal']
    ))
    elements.append(Paragraph(
        f'Teléfono: {venta.cliente_telefono or "No registrado"}',
        styles['Normal']
    ))
    elements.append(Paragraph(
        f'Vendedor: {venta.vendedor.get_full_name() or venta.vendedor.username}',
        styles['Normal']
    ))
    elements.append(Paragraph(
        f'Método de pago: {venta.get_metodo_pago_display()}',
        styles['Normal']
    ))

    elements.append(Spacer(1, 18))

    data = [['Producto', 'Cantidad', 'Precio unitario', 'Subtotal']]

    for detalle in venta.detalles.all():
        data.append([
            detalle.producto_nombre,
            str(detalle.cantidad),
            formato_pesos_pdf(detalle.precio_unitario),
            formato_pesos_pdf(detalle.subtotal)
        ])

    table = Table(data, colWidths=[7 * cm, 3 * cm, 4 * cm, 4 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#14532d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph(
        f'Subtotal: {formato_pesos_pdf(venta.subtotal)}',
        styles['Normal']
    ))
    elements.append(Paragraph(
        f'Descuento: {formato_pesos_pdf(venta.descuento)}',
        styles['Normal']
    ))
    elements.append(Paragraph(
        f'Total: {formato_pesos_pdf(venta.total)}',
        styles['Heading2']
    ))

    if venta.observaciones:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph('Observaciones:', styles['Heading3']))
        elements.append(Paragraph(venta.observaciones, styles['Normal']))

    doc.build(elements)

    return response


@login_required
@admin_required
def reporte_resumen_inventario_pdf(request):
    productos = Producto.objects.select_related('categoria', 'proveedor')
    total_productos = productos.count()
    productos_activos = productos.filter(activo=True).count()
    stock_bajo = productos.filter(stock__gt=0, stock__lte=F('stock_minimo')).count()
    agotados = productos.filter(stock=0).count()
    sin_movimiento = productos.annotate(
        total_movimientos=Count('movimientos')
    ).filter(total_movimientos=0).count()

    valor_inventario = Decimal('0')
    for producto in productos:
        valor_inventario += producto.precio * producto.stock

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte-resumen-inventario.pdf"'

    fecha = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %I:%M %p')
    doc, styles, elements = crear_documento_pdf(
        response,
        'Reporte de resumen de inventario',
        f'Generado el {fecha}'
    )

    resumen = [
        ['Indicador', 'Valor'],
        ['Total productos', str(total_productos)],
        ['Productos activos', str(productos_activos)],
        ['Stock bajo', str(stock_bajo)],
        ['Agotados', str(agotados)],
        ['Productos sin movimiento', str(sin_movimiento)],
        ['Valor total del inventario', formato_pesos_pdf(valor_inventario)],
    ]

    elements.append(aplicar_estilo_tabla(Table(resumen, colWidths=[9 * cm, 7 * cm])))
    elements.append(Spacer(1, 18))
    elements.append(Paragraph('Productos con stock bajo o agotado', styles['Heading3']))

    productos_criticos = productos.filter(
        Q(stock=0) | Q(stock__lte=F('stock_minimo'))
    ).order_by('stock', 'nombre')[:35]

    data = [['Producto', 'Categoria', 'Stock', 'Minimo', 'Valor']]

    for producto in productos_criticos:
        data.append([
            producto.nombre,
            producto.categoria.nombre if producto.categoria else 'Sin categoria',
            str(producto.stock),
            str(producto.stock_minimo),
            formato_pesos_pdf(producto.precio * producto.stock),
        ])

    if len(data) == 1:
        data.append(['Sin productos criticos', '-', '-', '-', '-'])

    elements.append(aplicar_estilo_tabla(Table(
        data,
        colWidths=[5.4 * cm, 4.2 * cm, 2.2 * cm, 2.2 * cm, 3 * cm]
    )))

    doc.build(elements)
    return response


@login_required
@admin_required
def reporte_distribucion_categorias_pdf(request):
    total_productos = Producto.objects.count()
    categorias = Categoria.objects.annotate(
        total_categoria=Count('productos')
    ).filter(
        total_categoria__gt=0
    ).order_by('-total_categoria', 'nombre')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte-distribucion-categorias.pdf"'

    fecha = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %I:%M %p')
    doc, styles, elements = crear_documento_pdf(
        response,
        'Reporte de distribucion por categoria',
        f'Generado el {fecha}'
    )

    data = [['Categoria', 'Productos', 'Participacion']]

    for categoria in categorias:
        if total_productos:
            porcentaje = (categoria.total_categoria / total_productos) * 100
        else:
            porcentaje = 0

        data.append([
            categoria.nombre,
            str(categoria.total_categoria),
            f'{porcentaje:.1f}%'.replace('.', ','),
        ])

    if len(data) == 1:
        data.append(['Sin categorias con productos', '0', '0%'])

    elements.append(aplicar_estilo_tabla(Table(
        data,
        colWidths=[9 * cm, 4 * cm, 4 * cm]
    )))
    elements.append(Spacer(1, 14))
    elements.append(Paragraph(f'Total de productos registrados: {total_productos}', styles['Normal']))

    doc.build(elements)
    return response


@login_required
@admin_required
def vendedor_lista(request):
    vendedores = User.objects.all().order_by('username')

    return render(request, 'inventario/vendedores_lista.html', {
        'vendedores': vendedores
    })


@login_required
@admin_required
def vendedor_crear(request):
    if request.method == 'POST':
        form = VendedorForm(request.POST)

        if form.is_valid():
            vendedor = form.save(commit=False)
            vendedor.is_staff = False
            vendedor.is_superuser = False
            vendedor.is_active = True
            vendedor.save()

            messages.success(request, 'Vendedor creado correctamente.')
            return redirect('vendedor_lista')
    else:
        form = VendedorForm()

    return render(request, 'inventario/vendedor_form.html', {
        'form': form,
        'titulo': 'Agregar vendedor',
        'volver_url': reverse('vendedor_lista')
    })
