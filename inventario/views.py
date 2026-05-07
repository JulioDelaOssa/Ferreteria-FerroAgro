from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AjusteStockForm, ProductoForm
from .models import Producto


@login_required
def home(request):
    return render(request, 'inventario/dashboard.html')

@login_required
def producto_lista(request):
    productos = Producto.objects.select_related('categoria', 'proveedor').all()

    return render(request, 'inventario/producto_lista.html', {
        'productos': productos
    })

@login_required
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('producto_lista')
    else:
        form = ProductoForm()

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'titulo': 'Nuevo producto'
    })

@login_required
def producto_editar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)

        if form.is_valid():
            form.save()
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'titulo': 'Editar producto'
    })

@login_required
def producto_eliminar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        producto.delete()
        return redirect('producto_lista')

    return render(request, 'inventario/producto_confirmar_eliminar.html', {
        'producto': producto
    })

@login_required
def inventario_lista(request):
    productos = Producto.objects.select_related('categoria').all()

    return render(request, 'inventario/inventario_lista.html', {
        'productos': productos
    })


@login_required
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
                return redirect('inventario_lista')
    else:
        form = AjusteStockForm()

    return render(request, 'inventario/ajustar_stock.html', {
        'form': form,
        'producto': producto
    })