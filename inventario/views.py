from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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