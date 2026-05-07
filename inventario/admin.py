from django.contrib import admin
from .models import Categoria, DetalleVenta, Producto, Proveedor, Venta, Movimientos

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'contacto', 'telefono', 'email')
    search_fields = ('nombre', 'email')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'stock', 'categoria', 'proveedor')
    list_filter = ('categoria', 'proveedor')
    search_fields = ('nombre',)

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendedor', 'fecha', 'total')
    list_filter = ('fecha', 'vendedor')
    search_fields = ('vendedor__username',)
    inlines = [DetalleVentaInline]

@admin.register(Movimientos)
class MovimientosAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'tipo', 'cantidad', 'usuario', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('producto__nombre', 'motivo', 'usuario__username')