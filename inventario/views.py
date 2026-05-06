from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProductoForm
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