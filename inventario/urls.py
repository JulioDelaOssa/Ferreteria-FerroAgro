from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('post-login/', views.post_login, name='post_login'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('productos/', views.producto_lista, name='producto_lista'),
    path('productos/crear/', views.producto_crear, name='producto_crear'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),

    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),

    path('proveedores/', views.proveedor_lista, name='proveedor_lista'),
    path('proveedores/crear/', views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/<int:pk>/editar/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_eliminar, name='proveedor_eliminar'),

    path('inventario/', views.inventario_lista, name='inventario_lista'),
    path('inventario/<int:pk>/ajustar/', views.ajustar_stock, name='ajustar_stock'),

    path('ventas/', views.ventas_panel, name='ventas_panel'),
    path('ventas/nueva/', views.venta_nueva, name='venta_nueva'),
    path('ventas/<int:pk>/', views.venta_detalle, name='venta_detalle'),
    path('ventas/<int:pk>/pdf/', views.factura_pdf, name='factura_pdf'),

    path('vendedores/', views.vendedor_lista, name='vendedor_lista'),
    path('vendedores/crear/', views.vendedor_crear, name='vendedor_crear'),
]