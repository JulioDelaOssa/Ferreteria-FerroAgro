from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from functools import wraps
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AjusteStockForm, ProductoForm, VendedorForm, VentaForm
from .models import DetalleVenta, Producto, Venta


def es_administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if es_administrador(request.user):
            return view_func(request, *args, **kwargs)

        return redirect('ventas_panel')

    return wrapped_view


@login_required
def post_login(request):
    if es_administrador(request.user):
        return redirect('dashboard')

    return redirect('ventas_panel')


@admin_required
def home(request):
    total_productos = Producto.objects.count()
    stock_disponible = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0
    stock_bajo = Producto.objects.filter(stock__gt=0, stock__lte=5).count()
    productos_agotados = Producto.objects.filter(stock=0).count()
    total_ventas = Venta.objects.count()
    total_vendedores = User.objects.filter(is_staff=False, is_superuser=False).count()
    ultimas_ventas = Venta.objects.select_related('vendedor').order_by('-fecha')[:5]
    productos_stock_bajo = Producto.objects.select_related('categoria').filter(stock__lte=5).order_by('stock')[:5]

    total_ingresos = Venta.objects.aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'inventario/dashboard.html', {
        'total_productos': total_productos,
        'stock_disponible': stock_disponible,
        'stock_bajo': stock_bajo,
        'productos_agotados': productos_agotados,
        'total_ventas': total_ventas,
        'total_vendedores': total_vendedores,
        'ultimas_ventas': ultimas_ventas,
        'productos_stock_bajo': productos_stock_bajo,
        'total_ingresos': total_ingresos
    })


@admin_required
def producto_lista(request):
    productos = Producto.objects.select_related('categoria', 'proveedor').all()

    return render(request, 'inventario/producto_lista.html', {
        'productos': productos
    })


@admin_required
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Producto registrado correctamente.')
            return redirect('producto_lista')
    else:
        form = ProductoForm()

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'titulo': 'Nuevo producto'
    })


@admin_required
def producto_editar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)

        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'titulo': 'Editar producto'
    })


@admin_required
def producto_eliminar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('producto_lista')

    return render(request, 'inventario/producto_confirmar_eliminar.html', {
        'producto': producto
    })


@admin_required
def inventario_lista(request):
    productos = Producto.objects.select_related('categoria').all()

    return render(request, 'inventario/inventario_lista.html', {
        'productos': productos
    })


@admin_required
def ajustar_stock(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = AjusteStockForm(request.POST)

        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']

            if tipo == 'salida' and cantidad > producto.stock:
                form.add_error('cantidad', 'La salida no puede ser mayor al stock actual.')
            else:
                if tipo == 'entrada':
                    producto.stock += cantidad

                if tipo == 'salida':
                    producto.stock -= cantidad

                producto.save()
                messages.success(request, 'Stock actualizado correctamente.')
                return redirect('inventario_lista')
    else:
        form = AjusteStockForm()

    return render(request, 'inventario/ajustar_stock.html', {
        'form': form,
        'producto': producto
    })


@login_required
def ventas_panel(request):
    productos = Producto.objects.select_related('categoria').filter(stock__gt=0).order_by('nombre')

    if es_administrador(request.user):
        ventas = Venta.objects.select_related('vendedor').all()[:8]
    else:
        ventas = Venta.objects.select_related('vendedor').filter(vendedor=request.user)[:8]

    return render(request, 'inventario/ventas_panel.html', {
        'productos': productos,
        'ventas': ventas
    })


@login_required
def venta_crear(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = VentaForm(request.POST)

        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']

            if cantidad > producto.stock:
                form.add_error('cantidad', 'No hay stock suficiente para realizar la venta.')
            else:
                with transaction.atomic():
                    producto = Producto.objects.select_for_update().get(id=producto.id)

                    if cantidad > producto.stock:
                        form.add_error('cantidad', 'No hay stock suficiente para realizar la venta.')
                    else:
                        subtotal = producto.precio * cantidad
                        venta = Venta.objects.create(vendedor=request.user, total=subtotal)
                        DetalleVenta.objects.create(
                            venta=venta,
                            producto=producto,
                            producto_nombre=producto.nombre,
                            cantidad=cantidad,
                            precio_unitario=producto.precio,
                            subtotal=subtotal
                        )
                        producto.stock -= cantidad
                        producto.save()
                        messages.success(request, 'Venta registrada correctamente.')
                        return redirect('ventas_panel')
    else:
        form = VentaForm()

    return render(request, 'inventario/venta_form.html', {
        'form': form,
        'producto': producto
    })


@admin_required
def vendedores_lista(request):
    vendedores = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')

    return render(request, 'inventario/vendedores_lista.html', {
        'vendedores': vendedores
    })


@admin_required
def vendedor_crear(request):
    if request.method == 'POST':
        form = VendedorForm(request.POST)

        if form.is_valid():
            vendedor = form.save(commit=False)
            vendedor.is_staff = False
            vendedor.is_superuser = False
            vendedor.save()
            grupo, creado = Group.objects.get_or_create(name='Vendedor')
            vendedor.groups.add(grupo)
            messages.success(request, 'Vendedor creado correctamente.')
            return redirect('vendedores_lista')
    else:
        form = VendedorForm()

    return render(request, 'inventario/vendedor_form.html', {
        'form': form
    })