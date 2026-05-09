from django.contrib import admin

from .models import Categoria, DetalleVenta, Movimientos, Producto, Proveedor, Venta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'contacto', 'telefono', 'email', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'contacto', 'telefono', 'email']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'proveedor', 'precio', 'stock', 'stock_minimo', 'activo']
    list_filter = ['activo', 'categoria', 'proveedor']
    search_fields = ['nombre', 'descripcion']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente_nombre', 'vendedor', 'metodo_pago', 'estado', 'total', 'fecha']
    list_filter = ['estado', 'metodo_pago', 'fecha']
    search_fields = ['cliente_nombre', 'cliente_documento', 'cliente_telefono']
    inlines = [DetalleVentaInline]


@admin.register(Movimientos)
class MovimientosAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'usuario', 'fecha']
    list_filter = ['tipo', 'fecha']
    search_fields = ['producto__nombre', 'motivo']